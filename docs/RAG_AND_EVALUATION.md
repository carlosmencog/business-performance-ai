# Retrieval, evaluation, and limitations

## What is implemented

The knowledge layer tokenizes the question and active documents, expands a few explicit synonyms, and calculates a transparent TF-IDF-like score. It returns the document version, effective date, department, matched terms, score, and text used in the answer.

This is RAG in the narrow sense: retrieval augments the answer with external evidence. It is not embedding-based semantic RAG and the UI says so.

## Regression evaluation

The automated suite validates:

| Scenario | Expected behavior |
| --- | --- |
| Response-time policy | At least one versioned citation returns |
| Revenue question | The governed KPI tool is selected |
| Historical response policy | The superseded version is never cited |

For a production corpus, retain a versioned JSONL evaluation set with question, metadata filters, expected chunk IDs, and expected refusal behavior. Track recall@k, citation precision, grounded-answer rate, p95 latency, tool failure rate, and cost per answer. Do not claim those metrics until the evaluation set and results exist.

## Known limitations

- The documents and business data are synthetic.
- The retrieval score is lexical; paraphrases can miss relevant material.
- No external LLM is called. The answer concatenates retrieved evidence rather than producing a free-form executive summary.
- Traces are process-memory only and disappear when the service restarts.
