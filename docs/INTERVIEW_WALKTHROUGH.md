# Interview walkthrough

## Two-minute demo

1. Open the dashboard and state that its data is synthetic and deterministic.
2. Ask: `What was revenue in the last 30 days?` Point out the tool name `governed_kpi_query`, the calculated result, and its allow-list guardrail.
3. Ask: `What happens when response time exceeds target?` Point out the policy citation, version, effective date, matched terms, and retrieval score.
4. Open the trace disclosure and explain that it records what the system did, rather than hiding the decision path.

## Talking points

- “I chose a deterministic router instead of an agent framework because the workflow has two bounded tools and no need for dynamic planning.”
- “The model layer, if added, would not write SQL. It could only select a typed tool and consume its result.”
- “Version and effective-date metadata prevent an old policy from being presented as active.”
- “I would use pgvector when semantic retrieval is justified by a larger corpus and a measured evaluation set.”

## Honest framing

Say: “I built this portfolio project to demonstrate my AI Engineering architecture and delivery skills.” Do not say that it processed real company data or was used in production.
