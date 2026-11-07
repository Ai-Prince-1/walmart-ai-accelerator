================================================================================
PRD: Vendor Contract SLA Risk Auditor (Sprint 1)
CATEGORY: SUPPLY CHAIN PROCUREMENT
NOTE: Independent learning project. Not affiliated with or endorsed by Walmart Inc.
      Figures below are planning assumptions and targets, not measured results.
================================================================================
Product: Vendor Contract Risk & SLA Compliance Auditor
In high-volume retail supply chains, manually auditing thousands of supplier Master Service Agreements (MSAs) for compliance with strict metrics like OTIF (On-Time In-Full) is an operational bottleneck. A single missed non-compliance liability clause can drain millions from retail margins.
📋 The Strategic Business Blueprint
1. The P&L Holder & Target Audience
The Executive Owner (hypothetical): VP of Supply Chain Procurement at a large retailer.
The User: Supply Chain Procurement Managers and Sourcing Analysts.
2. The Core Value Proposition & ROI
Assumption: manually reviewing a 60-page vendor contract for SLA risk points takes an analyst about 3 hours. At scale, this prevents 100% audit coverage of secondary and tertiary vendors, leading to leakage in contractually owed penalties.
The AI Solution: Reduce the initial ingestion and risk-flagging time from 3 hours to under 45 seconds per contract.
Target Financial ROI: Capture an estimated 1.5–3% in un-enforced OTIF penalty leakages across mid-tier suppliers, converting operational oversight directly back into gross margin.
3. Core Operational Definitions
Key operational definitions:
OTIF (On-Time In-Full): The supply chain gold standard. A supplier must deliver the exact quantity of goods ordered within a strict delivery window. Failing to deliver "on time" or "in full" disrupts store shelves and triggers automated fee penalties.
SLA (Service Level Agreement): The binding section of the contract defining these performance metrics, measurement windows, and corresponding financial penalties.
Liability Caps: The absolute maximum financial penalty a vendor can be charged in a given fiscal period, typically expressed as a percentage of total purchase order value (e.g., capped at 15%).
📊 AI Success & Performance Metrics
Success metrics (targets, defined before building; see evals/ for what has been measured so far):
+------------------------------------+------------------------------------+
| Metric                             | Enterprise Target Target           |
+------------------------------------+------------------------------------+
| Precision (Risk Flagging)          | > 94% (Minimize false positives to |
|                                    | protect analyst time)              |
+------------------------------------+------------------------------------+
| Recall (Risk Flagging)             | 99.9% (Missed risk clauses equal   |
|                                    | uncaptured financial leakage)      |
+------------------------------------+------------------------------------+
| Latency / Cost Budget              | < 15 seconds per document /        |
|                                    | Target cost: < $0.02 per contract  |
+------------------------------------+------------------------------------+
