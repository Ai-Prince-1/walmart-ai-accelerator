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
