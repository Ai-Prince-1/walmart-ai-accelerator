"""Vendor contract SLA risk auditor.

Pipeline
  1. Split the contract into pages.
  2. Token gate (free, local): keep only pages that mention BOTH a delivery
     metric (e.g. OTIF) AND a financial remedy (e.g. chargeback, penalty).
  3. Stage 1 (LLM): for each kept page, extract metric_pct, trigger_window and
     penalty_pct as strict JSON, then validate the keys.
  4. Stage 2 (rules, free): flag any penalty below the buyer's policy floor
     (default 3%), because a weak penalty means under-recovered losses.

Run
  python contract_auditor.py --dry-run            # gate only, no API key needed
  GROQ_API_KEY=... python contract_auditor.py     # full audit via Groq
"""
import argparse
import json
import os
import re
import urllib.request

MODEL_STRING = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
PAGE_MARKER = "--- START OF PAGE"

# One shared vocabulary for the token gate. A page must contain at least one
# metric term AND one remedy term. Broad remedy terms protect recall: vendors
# often write "chargeback" or "offset" instead of "penalty".
METRIC_KEYWORDS = ["otif", "on-time", "in-full", "fill-rate", "fill rate", "shipment", "delivery score"]
RISK_KEYWORDS = ["penalty", "fee", "liquidated", "chargeback", "deduction", "offset",
                 "withhold", "remedy", "remedies", "damages"]

SYSTEM_PROMPT = (
    "Extract SLA metrics. Output ONLY raw JSON matching keys: 'metric_pct', "
    "'trigger_window', 'penalty_pct'. No markdown wrappers or conversational text."
)
REQUIRED_KEYS = {"metric_pct", "trigger_window", "penalty_pct"}


# ---------------------------------------------------------------------------
# Local, zero-cost steps
# ---------------------------------------------------------------------------
def clean_and_minify_text(raw_text: str) -> str:
    """Collapse whitespace to shrink the prompt."""
    return re.sub(r"\s+", " ", raw_text).strip()


def boolean_token_gate(text: str) -> bool:
    """True if the text names a delivery metric AND a financial remedy."""
    t = text.lower()
    return any(m in t for m in METRIC_KEYWORDS) and any(r in t for r in RISK_KEYWORDS)


def split_pages(raw_contract: str) -> list:
    """Split on page markers; drop empty fragments."""
    return [p for p in raw_contract.split(PAGE_MARKER) if p.strip()]


def parse_percent(value):
    """Pull the first number out of values like 3, '3%', '1.5 percent' or
    '3% of gross invoice value'. Returns None if there is no number."""
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d+(?:\.\d+)?", str(value or ""))
    return float(match.group()) if match else None


# ---------------------------------------------------------------------------
# Stage 1: LLM extraction
# ---------------------------------------------------------------------------
def call_groq(clause: str) -> dict:
    """Send one clause to Groq and return the parsed JSON body."""
    api_key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY is not set. Use --dry-run to test without it.")
    payload = {
        "model": MODEL_STRING,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Clause: {clause}"},
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(GROQ_API_URL, data=json.dumps(payload).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "contract-risk-auditor/1.1")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_sla_metrics(contract_clause: str, llm=call_groq) -> dict:
    """Gate, minify, call the model, and validate the JSON it returns."""
    if not boolean_token_gate(contract_clause):
        return {"status": "SKIPPED", "reason": "No metric + remedy terms. $0 cost."}
    try:
        body = llm(clean_and_minify_text(contract_clause))
        usage = body.get("usage", {})
        print(f"📊 [FinOps Ledger] prompt={usage.get('prompt_tokens')} "
              f"completion={usage.get('completion_tokens')} total={usage.get('total_tokens')}")
        output = json.loads(body["choices"][0]["message"]["content"])
    except EnvironmentError:
        raise
    except Exception as e:  # network errors, malformed JSON
        return {"status": "ERROR", "details": str(e)}
    if not isinstance(output, dict) or not REQUIRED_KEYS.issubset(output):
        return {"status": "SCHEMA_ERROR", "raw": output}
    output["status"] = "SUCCESS"
    return output


# ---------------------------------------------------------------------------
# Stage 2: deterministic rules
# ---------------------------------------------------------------------------
def score_risk(extracted: dict, legal_floor_pct: float = 3.0) -> dict:
    """Flag penalties below the policy floor (a weak penalty under-recovers losses)."""
    if extracted.get("status") != "SUCCESS":
        return {"risk_score": "UNKNOWN", "reason": f"Stage 1 status: {extracted.get('status')}"}
    penalty = parse_percent(extracted.get("penalty_pct"))
    if penalty is None:
        return {"risk_score": "FAIL_COMPUTE", "reason": f"No number in penalty_pct: {extracted.get('penalty_pct')!r}"}
    if penalty < legal_floor_pct:
        return {"risk_score": "CRITICAL_FLAG", "penalty_pct": penalty,
                "reason": f"Penalty {penalty}% is below the {legal_floor_pct}% policy floor."}
    return {"risk_score": "COMPLIANT_PASS", "penalty_pct": penalty,
            "reason": f"Penalty {penalty}% meets the {legal_floor_pct}% policy floor."}


# ---------------------------------------------------------------------------
# End to end
# ---------------------------------------------------------------------------
SEVERITY = ["CRITICAL_FLAG", "FAIL_COMPUTE", "UNKNOWN", "COMPLIANT_PASS"]


def execute_audit_pipeline(raw_contract: str, llm=call_groq, dry_run=False, legal_floor_pct=3.0) -> dict:
    """Map: gate each page and audit the ones that pass. Reduce: report the
    worst finding across pages."""
    pages = split_pages(raw_contract)
    viable = [(i + 1, p) for i, p in enumerate(pages) if boolean_token_gate(p)]
    print(f"📋 {len(pages)} pages; token gate passed {len(viable)} to the model.")

    if dry_run or not viable:
        return {"pages": len(pages), "gated_pages": [n for n, _ in viable], "findings": [],
                "verdict": "DRY_RUN" if dry_run else "CLEAN"}

    findings = []
    for page_no, page in viable:
        extracted = extract_sla_metrics(page, llm=llm)
        verdict = score_risk(extracted, legal_floor_pct)
        findings.append({"page": page_no, "extracted": extracted, **verdict})

    worst = min(findings, key=lambda f: SEVERITY.index(f["risk_score"]))["risk_score"]
    return {"pages": len(pages), "gated_pages": [n for n, _ in viable], "findings": findings, "verdict": worst}


def main():
    ap = argparse.ArgumentParser(description="Audit a vendor contract for weak SLA penalties.")
    ap.add_argument("path", nargs="?", default="heavy_vendor_agreement.txt", help="contract text file")
    ap.add_argument("--dry-run", action="store_true", help="run the free token gate only (no API key)")
    ap.add_argument("--floor", type=float, default=3.0, help="policy floor for penalty %% (default 3)")
    args = ap.parse_args()

    with open(args.path, encoding="utf-8") as f:
        raw = f.read()
    result = execute_audit_pipeline(raw, dry_run=args.dry_run, legal_floor_pct=args.floor)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
