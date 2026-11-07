# Walmart AI Accelerator (independent portfolio): Vendor Contract Risk Auditor

![tests](https://github.com/Ai-Prince-1/walmart-ai-accelerator/actions/workflows/tests.yml/badge.svg)

An independent AI product-management portfolio built around the supply-chain problems a retailer like Walmart faces. Each sprint pairs a product spec with working code, cost math and an evaluation.

> **Independent learning project.** Not affiliated with or endorsed by Walmart Inc. The sample contract is synthetic. Business figures are stated assumptions or projections unless marked as measured.

> **Status (Nov 2026): on hold.** The plan was to ship a new MVP each week. Sprint 1 shipped and is tested; Sprints 2+ were not started and the project is paused while I focus on other work. Sprint 1 remains runnable as-is.

## How it works (plain English)

| Layer | What it is | In this project |
|---|---|---|
| **1. Input** | A contract as a plain-text file | `heavy_vendor_agreement.txt`, a synthetic 60-page supplier agreement |
| **2. Processing** | A single Python script, no installs needed | Free keyword filter picks the pages worth reading → an AI model (Llama 3.1 8B, hosted by Groq) pulls out the penalty terms as structured data → plain code checks them against the 3% policy floor |
| **3. Output** | A report in the terminal | Which pages were checked, what was found, and a verdict: `CRITICAL_FLAG` or `COMPLIANT_PASS` |

There is no website or server; it's a command-line tool. The Groq API key is read from your environment, never stored in the repo.

## Sprint 1: Vendor contract SLA risk auditor

**Problem.** Supplier contracts hide delivery-performance (OTIF) penalties inside long legal documents. A penalty set too low means the retailer under-recovers losses from late or short shipments. Reviewing every contract by hand doesn't scale.

**Approach.** Send the model only the pages that matter, then let plain code make the final call.

```
contract.txt ─► split into pages ─► token gate (free) ─► LLM extraction ─► rules engine (free) ─► verdict
                                    metric AND remedy     strict JSON +       penalty below the
                                    terms on the page     key validation      3% floor → CRITICAL_FLAG
```

| Step | What it does | Cost |
|---|---|---|
| Token gate | Keeps a page only if it names a delivery metric (OTIF, fill rate…) **and** a remedy (penalty, chargeback, offset…) | $0 |
| Extraction | `llama-3.1-8b-instant` on Groq returns `metric_pct`, `trigger_window`, `penalty_pct` as JSON; missing keys are rejected | fractions of a cent |
| Rules | Flags any penalty below the policy floor (default 3%) | $0 |

### Run it

No dependencies beyond Python 3.10+ (the code uses only the standard library).

```bash
python contract_auditor.py --dry-run          # token gate only, no API key needed
export GROQ_API_KEY=your_key                  # free key at console.groq.com
python contract_auditor.py                    # full audit of heavy_vendor_agreement.txt
python contract_auditor.py my_contract.txt --floor 2.5
```

On the 60-page synthetic contract, the gate sends **1 of 60 pages** to the model (page 42, which holds a 1.5% chargeback), and the rules flag it as `CRITICAL_FLAG`.

### What's been measured

| Check | Result |
|---|---|
| Offline test suite (`pytest -q`; model stubbed) | 15 passing, run in CI |
| Token gate on a 20-clause labeled set (`python evals/run_gate_eval.py`) | **80% recall, 89% precision** |

The gate catches defensive wording like "chargeback deduction" and "offset against invoices". It misses phrasings with no keyword ("compliance charge", "reduce the amount payable"), and it over-triggers on one informational sentence. That's the honest ceiling of a keyword filter. The next step is a cheap semantic gate (embeddings or a small classifier) to push recall toward the 99.9% target in the PRD.

### Cost model

`sprint1_finops_architecture.md` projects about **$248 per 10M clause evaluations**, against $95,000 for sending whole documents to a larger model. About 94% of that saving comes from gating and minification alone; the rest comes from using a smaller model. These are projections, not billed usage.

### Files

| File | Purpose |
|---|---|
| [`contract_auditor.py`](./contract_auditor.py) | The pipeline: gate → extract → validate → score |
| [`sprint1_contract_prd.md`](./sprint1_contract_prd.md) | PRD: user, value hypothesis, success metrics |
| [`sprint1_finops_architecture.md`](./sprint1_finops_architecture.md) | Token cost model and prompt design |
| [`foundations/technical_deep_dive.md`](./foundations/technical_deep_dive.md) | Domain notes: OTIF clauses, keyword strategy |
| [`sprint1_demo_deck.md`](./sprint1_demo_deck.md) | Three-slide pitch outline |
| [`evals/`](./evals) | Labeled clauses and the gate evaluation |
| [`tests/`](./tests) | Offline unit and end-to-end tests |
| `heavy_vendor_agreement.txt` | Synthetic 60-page contract (boilerplate plus one SLA clause) |
| `EVAL_LOG.csv` | Illustrative sample of the per-clause cost ledger format |
| `STATE_COMMIT_WEEK_01.md` | Sprint 1 status and backlog |

## Roadmap

| Sprint | Focus | Status |
|---|---|---|
| 1 | Procurement: contract SLA risk auditor | Built, tested, gate measured |
| 2 | Fulfillment: route optimization with live traffic and weather inputs | On hold |
| 3 | Grocery: perishable inventory and markdown timing | On hold |

## License

MIT. See [LICENSE](./LICENSE).
