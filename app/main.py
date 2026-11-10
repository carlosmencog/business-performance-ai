"""Business Performance AI API: deterministic tools, evidence-grounded knowledge, observable runs."""
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import logging, os, re, time, uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from .seed import seed, DB_PATH
from .knowledge import retrieve

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bpa")
ROOT = Path(__file__).resolve().parents[1]; TRACES = deque(maxlen=100)
DB_TIMEOUT_SECONDS = 5; RETRY_DELAYS_SECONDS = (.05, .1)
ALLOWED = {"revenue": "SUM(revenue)", "orders": "SUM(orders)", "response_time": "AVG(response_minutes)", "csat": "AVG(csat)", "fulfillment": "AVG(fulfillment_rate)"}
METRIC_LABELS = {"revenue":"revenue", "orders":"orders", "response_time":"average response time", "csat":"CSAT", "fulfillment":"fulfillment rate"}

@asynccontextmanager
async def lifespan(app):
    if not DB_PATH.exists(): seed()
    yield
app = FastAPI(title="Business Performance AI", version="1.0.0", lifespan=lifespan)
class KPIQuery(BaseModel):
    metric: Literal["revenue","orders","response_time","csat","fulfillment"]
    start_date: str = Field(pattern=r"^2027-\d\d-\d\d$")
    end_date: str = Field(pattern=r"^2027-\d\d-\d\d$")
class Ask(BaseModel):
    question: str = Field(min_length=4, max_length=500)
    as_of: str = Field(default="2027-04-30", pattern=r"^2027-\d\d-\d\d$")
def db():
    url = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    return create_engine(url, pool_pre_ping=True, connect_args={"timeout": DB_TIMEOUT_SECONDS} if url.startswith("sqlite") else {})
def read_scalar(stmt, params):
    """Retry only a read-only, transient database operation; writes need idempotency controls."""
    for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
        try:
            with db().connect() as c: return c.execute(stmt, params).scalar()
        except OperationalError:
            if attempt == len(RETRY_DELAYS_SECONDS): raise
            time.sleep(RETRY_DELAYS_SECONDS[attempt])
def metric(query: KPIQuery):
    stmt = text(f"SELECT {ALLOWED[query.metric]} AS value FROM daily_metrics WHERE metric_date BETWEEN :start AND :end")
    value = read_scalar(stmt, {"start":query.start_date,"end":query.end_date})
    if value is None: raise HTTPException(404, "No data exists for that period.")
    return round(float(value), 2)
def metric_intent(question: str):
    q = question.lower(); found = next((m for m in ALLOWED if re.search(rf"\b{m.replace('_','[ _-]?')}\b", q)), None)
    aliases = {"sales":"revenue", "income":"revenue", "satisfaction":"csat", "delivery":"fulfillment", "response time":"response_time", "orders":"orders"}
    found = found or next((v for k,v in aliases.items() if k in q), None)
    if not found: return None
    # Policy language belongs to retrieval even when it names a metric.
    if any(word in q for word in ("target", "exceed", "require", "required", "happens", "policy", "review")): return None
    # Avoid treating every metric mention as a data request.
    if not any(word in q for word in ("what was", "show", "average", "total", "last", "this month", "how much")): return None
    last_period = "last 30" in q or "last month" in q or "this month" in q
    return KPIQuery(metric=found, start_date="2027-03-31" if last_period else "2027-01-01", end_date="2027-04-29")
def kpi_explanation(q: KPIQuery, value: float):
    formatted = f"${value:,.0f}" if q.metric == "revenue" else f"{value:,.0f}" if q.metric == "orders" else f"{value:.1f} minutes" if q.metric == "response_time" else f"{value:.2f}" if q.metric == "csat" else f"{value:.1f}%"
    return f"For {q.start_date} to {q.end_date}, {METRIC_LABELS[q.metric]} was {formatted}. This number was calculated by the governed KPI tool."
@app.middleware("http")
async def trace(request: Request, call_next):
    started=time.perf_counter(); run_id=str(uuid.uuid4())[:8]
    try: response=await call_next(request)
    except Exception: log.exception("trace run_id=%s unhandled error", run_id); raise
    duration=round((time.perf_counter()-started)*1000); response.headers["X-Run-Id"] = run_id
    log.info("trace run_id=%s method=%s path=%s status=%s duration_ms=%s", run_id, request.method, request.url.path, response.status_code, duration); return response
@app.get("/")
def home(): return FileResponse(ROOT / "web" / "index.html")
@app.get("/api/health")
def health(): return {"status":"ok", "time":datetime.now(timezone.utc).isoformat(), "storage":"sqlite-demo"}
@app.get("/api/overview")
def overview():
    with db().connect() as c: rows=c.execute(text("SELECT metric_date,revenue,orders,response_minutes,csat,fulfillment_rate FROM daily_metrics ORDER BY metric_date")).mappings().all()
    last, prev=rows[-30:],rows[-60:-30]
    return {"cards":{"revenue":round(sum(x["revenue"] for x in last)),"orders":sum(x["orders"] for x in last),"response_time":round(sum(x["response_minutes"] for x in last)/30,1),"csat":round(sum(x["csat"] for x in last)/30,2)},"trend":[dict(x) for x in last],"comparison":{"revenue_change":round((sum(x["revenue"] for x in last)/sum(x["revenue"] for x in prev)-1)*100,1)}}
@app.post("/api/kpis")
def kpis(query: KPIQuery): return {"metric":query.metric, "value":metric(query), "source":"daily_metrics", "guardrail":"server-side metric allow-list + bound date parameters"}
@app.post("/api/ask")
def ask(body: Ask):
    started=time.perf_counter(); run_id=str(uuid.uuid4())[:8]; tools=[]; intent=metric_intent(body.question)
    if intent:
        value=metric(intent); tools.append({"name":"governed_kpi_query","status":"success","input":intent.model_dump(),"output":{"value":value}}); answer=kpi_explanation(intent,value); citations=[]
    else:
        sources=retrieve(body.question, as_of=body.as_of); tools.append({"name":"versioned_document_retrieval","status":"success","input":{"as_of":body.as_of,"limit":3},"output":{"results":len(sources)}})
        if not sources: answer="I could not find enough active internal evidence to answer that safely. Try asking about response time, CSAT, fulfillment, or revenue review."; citations=[]
        else: answer="Based on the active internal playbooks: " + " ".join(x["content"] for x in sources); citations=[{k:x[k] for k in ("id","title","version","effective_from","department","content","matched_terms","score")} for x in sources]
    run={"run_id":run_id,"at":datetime.now(timezone.utc).isoformat(),"question":body.question,"tools":tools,"citations":len(citations),"latency_ms":round((time.perf_counter()-started)*1000)}; TRACES.appendleft(run)
    return {"answer":answer,"citations":citations,"trace":run,"limitations":"Demo data and deterministic retrieval; no external LLM was used to generate this response."}
@app.get("/api/traces")
def traces(): return list(TRACES)
