> Illustrative pitch outline for a hypothetical buyer. Numbers are projections or targets unless marked as measured.

Slide 1: The Core Value Proposition
The Problem: Manually auditing complex, multi-page Master Service Agreements (MSAs) across thousands of secondary suppliers leads to critical risk oversights. Evaluating a single agreement takes roughly 3 hours of manual compliance labor (assumption). This operational bottleneck creates severe leakage in contractually owed penalties.
The AI Solution: An automated, token-gated contract ingestion engine that parses legal agreements, executes programmatic schema validation, and flags hidden structural risks in under 45 seconds per document.
Slide 2: Ruthless Token FinOps Unit Economics
The Strategic Engineering Breakthrough: Traditional, naive LLM deployments process complete documents through massive context windows, costing a modeled $95,000 per 10,000,000 transactions on a larger model.
Our Architecture: By enforcing a strict programmatic Boolean Token Gate and minifying whitespace via Regular Expressions, we screen out up to 85% of non-relevant boilerplate text before it ever hits an AI model.
The Bottom Line: The projected run-rate for 10,000,000 evaluations is about $248: 99.74% lower overall, of which about 94% comes from gating and minification and the rest from using a smaller model.
Slide 3: Model Guardrails & Data Performance
Precision/Recall Equilibrium: Target: 99.9% recall. Measured so far: the free keyword gate scores 80% recall and 89% precision on a 20-clause labeled set (evals/), catching "chargeback" and "offset" wording but missing phrasings like "compliance charge". Schema validation rejects malformed model output.
Enterprise Security Posture: The API key is read only from an environment variable, never stored in code, and the script fails with a clear error if it is missing.
