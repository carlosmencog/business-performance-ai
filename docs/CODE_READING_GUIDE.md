# Code reading guide

Use this file when studying the project with ChatGPT or preparing for an interview.

| File | Read it for | Key idea |
| --- | --- | --- |
| `app/seed.py` | Synthetic data generation | A fixed random seed makes demo data reproducible. |
| `app/main.py` | API, routing, safety, traces | Python owns every tool boundary; the model is never trusted to create SQL. |
| `app/knowledge.py` | RAG behavior | Metadata and active-version filtering happen before ranking. |
| `web/index.html` | User experience | It shows the answer, evidence, guardrail, and trace rather than hiding them. |
| `tests/test_api.py` | Regression coverage | Tests encode the safety and routing behavior that must not regress. |

## Suggested study sequence

1. Start with `README.md` and `docs/ARCHITECTURE.md`.
2. Read `seed.py`, then call `/api/overview`.
3. Read `metric_intent`, `metric`, and `read_scalar` in `main.py`. Explain the allow-list, bound parameters, timeout, and retry boundary in your own words.
4. Read `retrieve` in `knowledge.py`. Ask what happens to a superseded document and why it is filtered before the score.
5. Use the dashboard twice: once with a revenue question, once with a policy question. Compare their traces.

## Questions ChatGPT can help you answer

- “Explain the `metric_intent` function line by line, as if I know JavaScript but am learning Python.”
- “Why is the retry intentionally limited to read-only database work?”
- “Show how to replace the lexical score with pgvector without changing the API contract.”
- “Turn the test cases into interview questions and quiz me one at a time.”
