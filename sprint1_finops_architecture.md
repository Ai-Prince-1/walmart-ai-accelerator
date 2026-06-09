# SPRINT 1: Token FinOps Architecture & Unit Economics

## 1. System Architecture: Two-Stage Prompt Chaining
Instead of passing complete 60-page Master Service Agreements (MSAs) into a massive LLM context window, our microservice implements a strict programmatic filter followed by an optimized two-stage prompt chain.

* **Layer 1: Programmatic Boolean Gate (Cost: $0):** Filters out text blocks that do not contain core statutory terms (e.g., "OTIF", "SLA", "Penalty").
* **Layer 2: Extraction Stage (Model: Llama-3-8B via Groq):** Extracts raw metrics from the isolated text blocks and returns a minified, structured JSON payload.
* **Layer 3: Risk Evaluation Stage:** Triggered only if Layer 2 detects a metric falling below Walmart's corporate risk threshold.

---

## 2. Enterprise Cost Projection Matrix (10,000,000 Transactions)

### Scenario A: Naive Context-Heavy Architecture
* **Execution Strategy:** Shoves raw document sections and long conversational prompts directly into the model without text minification.
* **Average Payload:** 8,000 Input tokens, 500 Output tokens per transaction.
* **Blended Rates:** $1.00 per 1M Input tokens, $3.00 per 1M Output tokens.
* **Mathematical Calculation:**
    * *Input Cost:* 10,000,000 Tx × (8,000 / 1,000,000) × $1.00 = $80,000.00
    * *Output Cost:* 10,000,000 Tx × (500 / 1,000,000) × $3.00 = $15,000.00
* **Total Naive Run-Rate:** **$95,000.00**

### Scenario B: Optimized Token FinOps Architecture
* **Execution Strategy:** Programmatic token gating eliminates 85% of non-relevant text blocks. RegEx minifies remaining white spaces, and the system prompt is tightly compressed.
* **Average Payload:** 400 Input tokens, 60 Output tokens per transaction.
* **Blended Rates:** $0.05 per 1M Input tokens, $0.08 per 1M Output tokens.
* **Mathematical Calculation:**
    * *Input Cost:* 10,000,000 Tx × (400 / 1,000,000) × $0.05 = $200.00
    * *Output Cost:* 10,000,000 Tx × (60 / 1,000,000) × $0.08 = $48.00
* **Total FinOps Run-Rate:** **$248.00**

### Financial Summary
* **Gross Dollar Savings:** $94,752.00
* **Operational Cost Reduction:** 99.74% efficiency gain back to the Supply Chain Procurement P&L.

---

## 3. Minified System Prompt Blueprint

```json
[
  {
    "role": "system",
    "content": "Extract SLA metrics. Output ONLY raw JSON matching keys: 'metric_pct', 'trigger_window', 'penalty_pct'. No conversational text, headers, or markdown wrappers."
  }
]
