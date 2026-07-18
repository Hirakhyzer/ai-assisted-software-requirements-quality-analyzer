# Methodology

The analyzer uses a synthetic-first pipeline:

1. Generate fictional software requirements across functional, security, privacy, performance, compliance, operational, and data categories.
2. Normalize and parse each requirement.
3. Apply deterministic rule-based checks for ambiguous terms, missing acceptance criteria, missing actor, missing priority, missing linked tests, and unverifiable wording.
4. Detect conflict candidates through opposing policy phrases and domain overlap.
5. Audit traceability from requirement to design component and test case.
6. Compute requirement-level quality, risk, testability, completeness, traceability, and review-priority scores.
7. Produce CSV outputs, figures, a Markdown report, and a hash-chained audit record.

The initial implementation is intentionally transparent and auditable. Future work can add transformer-based semantic similarity, LLM-assisted critique, requirements ontology extraction, and integration with issue trackers.
