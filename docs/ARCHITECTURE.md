# Architecture

## System boundary

```text
Browser dashboard
  └─ POST /api/ask
      └─ deterministic router
          ├─ KPI intent → governed_kpi_query → SQLite demo database
          └─ policy intent → versioned_document_retrieval → active evidence + citations
```

There is no autonomous agent loop. The router is a small deterministic Python function because two tools are sufficient and their routing is easy to audit. LangGraph becomes appropriate only when a future version needs durable multi-step state, human approvals, or recovery across several external tools.

## Safety boundaries

1. A user can never submit SQL. Metric names are a Python `Literal` and map to a server-owned SQL allow-list.
2. Date values are bound parameters, never interpolated into SQL.
3. Document retrieval excludes `superseded` documents and documents effective after the requested date.
4. Answers return citations from the same objects used for retrieval.
5. The demo has no write tools, external actions, customer data, authentication, or external LLM key.

## Production evolution

Replace the SQLite demo database with managed PostgreSQL. Store documents, chunks, metadata, and `pgvector` embeddings in separate tables. Apply tenant and access filters before similarity ranking. Add authenticated user identity, structured trace storage, rate limiting, a secrets manager, and bounded provider timeouts/retries.
