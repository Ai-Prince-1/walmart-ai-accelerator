# Week 1: Foundational Extraction Audit

### 1. Target Metric (%)
* **Extracted Value:** 97.5%
* **Context:** Minimum allowable On-Time In-Full (OTIF) delivery score required from the supplier.

### 2. Trigger Window (Timeframe)
* **Extracted Value:** Two (2) consecutive quarters
* **Context:** The continuous duration of underperformance required before Walmart can contractually execute penalties.

### 3. Financial Penalty (%)
* **Extracted Value:** 3% fee of the gross value of all non-compliant purchase orders
* **Context:** The explicit financial clawback rate applied to the defective shipments.

### 4. 3-Word Token-Gating Keyword List
* **Keywords:** `OTIF`, `penalty`, `consecutive`
* **Engineering Logic:** If our fast Python script scans a paragraph and finds these exact words, it triggers a Boolean TRUE gate and routes this specific section to the LLM for deep risk analysis. If these words are missing, the paragraph is skipped entirely, saving token costs.

---

## REVISION 2 UPDATE: Expanded Procurement Vocabulary & Risk Safeguards

### 1. Living Configuration Framework
Following architectural review, the token-gating keyword arrays were expanded and modularized to eliminate False Negatives (protecting our 99.9% Recall target). Vendors frequently utilize mitigating legal prose to circumvent standard AI keyword sweeps.

* **Expanded Target Metric Keywords:** `fill-rate`, `shipment`, `delivery score` (in addition to `OTIF`, `on-time`, `in-full`).
* **Expanded Defensive Financial Risk Keywords:** `chargeback`, `deduction`, `offset`, `withhold`, `remedy`, `damages` (in addition to `penalty`, `fee`, `liquidated`).

### 2. Guardrails & Token Ledger Integrations
* **Fail Fast Security:** Stripped out fallback authentication strings to enforce zero-leak environment variable security.
* **Deterministic Schema Validation:** Added a programmatic key-subset validation layer to ensure the pipeline catches malformed JSON output before passing metrics downstream to databases.
* **FinOps Ledgering:** Implemented telemetry tracking to log `prompt_tokens`, `completion_tokens`, and `total_tokens` directly from the API response payload for auditing system cost efficiency.
