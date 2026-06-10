import os
import re
import json
import urllib.request

# ==========================================
# 1. CONFIGURATION, MODEL SETTINGS, & SECURITY
# ==========================================
# Fail Loud, Fail Early security mechanism
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("SECURITY ALERT: GROQ_API_KEY environment variable is missing. Execution halted.")

# Up-to-date high-speed inference engine string
MODEL_STRING = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Living configurations list for Walmart vocabulary alignment
METRIC_KEYWORDS = ["otif", "on-time", "in-full", "fill-rate", "shipment"]
RISK_KEYWORDS = ["penalty", "fee", "liquidated", "chargeback", "deduction", "offset", "withhold", "remedy", "damages"]

# ==========================================
# 2. DATA CLEANING & COMPRESSED TOKEN GATING
# ==========================================
def clean_and_minify_text(raw_text: str) -> str:
    """Uses RegEx to eliminate excess formatting and trailing spaces."""
    return re.sub(r'\s+', ' ', raw_text).strip()

def boolean_token_gate(text: str) -> bool:
    """Cost: $0. Evaluates extended retail risk terms before calling LLM."""
    text_lower = text.lower()
    has_metric = any(m in text_lower for m in METRIC_KEYWORDS)
    has_risk = any(r in text_lower for r in RISK_KEYWORDS)
    return has_metric and has_risk

# ==========================================
# 3. STAGE 1: METRIC EXTRACTION ENGINE
# ==========================================
def extract_sla_metrics(contract_clause: str) -> dict:
    """Extracts raw clause text into verified, minified JSON data."""
    if not boolean_token_gate(contract_clause):
        return {"status": "SKIPPED", "reason": "No corporate risk keywords triggered. $0 cost."}
    
    minified_clause = clean_and_minify_text(contract_clause)
    
    system_prompt = "Extract SLA metrics. Output ONLY raw JSON matching keys: 'metric_pct', 'trigger_window', 'penalty_pct'. No markdown wrappers or conversational text."
    user_prompt = f"Clause: {minified_clause}"
    
    payload = {
        "model": MODEL_STRING,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    req = urllib.request.Request(GROQ_API_URL)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {GROQ_API_KEY}")
    
    try:
        data = json.dumps(payload).encode("utf-8")
        with urllib.request.urlopen(req, data=data) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            
            # --- TOKEN FINOPS LEDGER LOGGING ---
            usage = res_body.get("usage", {})
            print(f"📊 [FinOps Ledger] Prompt Tokens: {usage.get('prompt_tokens')} | Completion Tokens: {usage.get('completion_tokens')} | Total: {usage.get('total_tokens')}")
            
            raw_output = json.loads(res_body["choices"][0]["message"]["content"])
            
            # --- SCHEMA VALIDATION STEP ---
            required_keys = {"metric_pct", "trigger_window", "penalty_pct"}
            if not required_keys.issubset(raw_output.keys()):
                return {"status": "SCHEMA_ERROR", "raw": raw_output}
                
            raw_output["status"] = "SUCCESS"
            return raw_output
            
    except Exception as e:
        return {"status": "ERROR", "details": str(e)}

# ==========================================
# 4. STAGE 2: RISK SCORING RULES ENGINE
# ==========================================
def score_risk(extracted_metrics: dict, legal_floor_pct: float = 3.0) -> dict:
    """Evaluates extracted metrics against Walmart's corporate legal floor."""
    if extracted_metrics.get("status") != "SUCCESS":
        return {"risk_score": "UNKNOWN", "reason": f"Bypassed. Stage 1 status: {extracted_metrics.get('status')}"}
    
    try:
        # Convert string percentages (e.g., '3%') to floats if model appended a symbol
        penalty_str = str(extracted_metrics.get("penalty_pct")).replace("%", "")
        penalty_val = float(penalty_str)
        
        # Operational business logic execution
        if penalty_val < legal_floor_pct:
            return {
                "risk_score": "CRITICAL_FLAG",
                "reason": f"Contract penalty rate ({penalty_val}%) falls below corporate mandate floor ({legal_floor_pct}%). Red line risk detected."
            }
        
        return {"risk_score": "COMPLIANT_PASS", "reason": "Penalty parameters sit within corporate legal thresholds."}
    except Exception as e:
        return {"risk_score": "FAIL_COMPUTE", "details": f"Data type evaluation error: {str(e)}"}

# ==========================================
# 5. END-TO-END SYSTEM TRIAL
# ==========================================
if __name__ == "__main__":
    print("🚀 Initializing Production Guarded Procurement Audit System...")
    
    # Test Case 1: Complex retail clause avoiding the word 'penalty'
    walmart_clause = """
    MASTER SERVICES AGREEMENT - SECTION 4.2: PERFORMANCE AND REMEDIES
The Sourcing Partner shall maintain operational excellence throughout the duration of this Agreement. Fulfillment execution shall be tracked via automated shipping logs, and the Sourcing Partner is contractually obligated to maintain a minimum 98.0% On-Time In-Full (OTIF) distribution threshold. Performance evaluations will be compiled systematically by Walmart's logistics platform. In the event that fulfillment metrics fall below this 98.0% standard for two consecutive quarters, the system will systematically flag the account. To remediate this supply deficiency, Walmart reserves the explicit right to assess a capital chargeback deduction equivalent to 1.5% against the total gross invoice valuation of all non-compliant shipments processed during the violation windows. This financial remedy will be executed as a direct offset against outstanding accounts payable balances.
    """
    
    print("\n--- Executing Stage 1 Extraction ---")
    extracted_data = extract_sla_metrics(walmart_clause)
    print("Stage 1 Output:", json.dumps(extracted_data, indent=2))
    
    print("\n--- Executing Stage 2 Risk Evaluation ---")
    audit_verdict = score_risk(extracted_data, legal_floor_pct=3.0)
    print("Stage 2 Final Verdict:", json.dumps(audit_verdict, indent=2))
