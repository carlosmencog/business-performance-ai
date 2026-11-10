# Business Performance AI

An explainable AI Engineering portfolio project for internal business performance: revenue, order volume, support response time, customer satisfaction, and fulfillment. It demonstrates a secure split between structured analytics and evidence-grounded internal knowledge.

> This is a synthetic, educational portfolio project. It does not represent professional production experience or use real company data.

## What works now

- Responsive executive dashboard using a reproducible 120-day synthetic dataset.
- Natural-language KPI questions such as `What was revenue in the last 30 days?`
- A typed, server-controlled KPI tool; no LLM-generated SQL and no arbitrary SQL endpoint.
- Versioned internal-policy retrieval with active/effective-date filtering, citations, matched terms, and inspectable scores.
- In-page run trace: routing decision, selected tool, input, outcome, citation count, and latency.
- Input validation, health endpoint, structured request logging, error feedback, Docker, and five automated API tests.

## Architecture

```text
Dashboard → FastAPI deterministic router
              ├─ governed KPI tool → parameterized SQL → synthetic analytics data
              └─ document retrieval → versioned active documents → citations
```

Read [architecture](docs/ARCHITECTURE.md), [retrieval and evaluation](docs/RAG_AND_EVALUATION.md), [interview walkthrough](docs/INTERVIEW_WALKTHROUGH.md), [deployment](docs/DEPLOYMENT.md), and the [code reading guide](docs/CODE_READING_GUIDE.md).

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8010
```

Open `http://localhost:8010`. Run the test suite with:

```powershell
pytest
```

## Useful demo questions

- `What was revenue in the last 30 days?`
- `What is the response time target?`
- `What happens when response time exceeds target?`
- `What happens when CSAT is below 4.30?`
- `When is a fulfillment review required?`

## Docker

```powershell
docker compose up --build
```

## Deliberate trade-offs

The project does not use LangGraph because its two routes are bounded, synchronous, and deterministic. It does not claim vector-semantic retrieval: the current retrieval is intentionally transparent and works without an API key. The production upgrade path is PostgreSQL + pgvector, metadata filters, reranking, an evaluation dataset, durable observability, authentication, and a bounded LLM synthesis step.

## Publish it

The GitHub and hosting path is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). Do not commit `.env` or real business data.
