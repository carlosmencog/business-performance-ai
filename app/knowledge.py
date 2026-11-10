"""Inspectable retrieval layer.

This MVP deliberately uses a hybrid lexical score instead of a hidden embedding provider.
It makes every retrieval decision explainable offline while preserving the seams needed for
pgvector embeddings later: chunks, metadata filters, a score, and a citation contract.
"""
from dataclasses import dataclass, asdict
import math
import re
from collections import Counter

TOKEN = re.compile(r"[a-z]{3,}")

@dataclass(frozen=True)
class Document:
    id: str
    title: str
    version: str
    effective_from: str
    status: str
    department: str
    content: str

DOCS = [
    Document("ops-playbook-v3", "Customer support operating playbook", "3.0", "2027-02-01", "active", "support",
      "Response-time target is under 45 minutes. If response time exceeds 55 minutes for three consecutive days, the operations lead must open an incident review and publish staffing coverage."),
    Document("cx-review-v2", "Customer experience weekly review", "2.1", "2027-01-15", "active", "customer-experience",
      "A CSAT score below 4.30 requires root-cause analysis. Teams should correlate response time, fulfillment rate, and ticket volume before proposing an intervention."),
    Document("fulfillment-v4", "Fulfillment reliability policy", "4.0", "2027-03-01", "active", "operations",
      "The fulfillment target is 96 percent or higher. A weekly result below 94 percent requires a carrier and inventory exception review."),
    Document("revenue-review-v1", "Commercial performance review guide", "1.4", "2027-01-01", "active", "commercial",
      "Revenue investigations should compare the current 30-day period with the previous 30 days, separate volume from average order value, and record any operational disruption before assigning a cause."),
    Document("ops-playbook-v2", "Customer support operating playbook", "2.0", "2026-01-01", "superseded", "support",
      "Historical policy: response-time target was under 60 minutes. Do not use for current operating decisions."),
]
SYNONYMS = {"reply":"response", "replies":"response", "slow":"response", "satisfaction":"csat", "delivery":"fulfillment", "sales":"revenue", "income":"revenue"}

def tokens(text: str) -> list[str]:
    return [SYNONYMS.get(t, t) for t in TOKEN.findall(text.lower())]

def retrieve(question: str, limit: int = 3, department: str | None = None, as_of: str = "2027-04-30") -> list[dict]:
    query = tokens(question); q_count = Counter(query)
    if not query: return []
    candidates = [d for d in DOCS if d.status == "active" and d.effective_from <= as_of and (not department or d.department == department)]
    total = len(candidates); scored = []
    for doc in candidates:
        doc_tokens = tokens(doc.title + " " + doc.content); counts = Counter(doc_tokens)
        score = sum((1 + math.log(counts[t])) * (1 + math.log(total / max(1, sum(t in tokens(x.content) for x in candidates)))) for t in q_count if counts[t])
        if score:
            item = asdict(doc); item["score"] = round(score, 3); item["matched_terms"] = sorted(set(query) & set(doc_tokens)); scored.append(item)
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:limit]
