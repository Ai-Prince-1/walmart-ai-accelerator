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
    
    # Construct native payload
    payload = {
        "model": MODEL_STRING,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    # Standard, compliant Python HTTP request execution
    req = urllib.request.Request(GROQ_API_URL)
    req.add_header("Content-Type", "application/json")
    
    # Ensure the token is passed cleanly without hidden spaces
    clean_token = str(GROQ_API_KEY).strip().replace('"', '').replace("'", "")
    req.add_header("Authorization", f"Bearer {clean_token}")
    
    # --- INDUSTRY-STANDARD COMPLIANCE FIX ---
    # Inform the API gateway exactly what application is connecting to it
    req.add_header("User-Agent", "WalmartAI-Accelerator-AuditEngine/1.0 (Compliance Component)")
    
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
def execute_audit_pipeline(raw_contract_data: str):
    """Runs the complete audit pipeline on a raw contract text payload using chunked map-reduce filtering."""
    print("\n--- Running Enterprise Map-Reduce Token Gate ---")
    
    # 1. SPLIT: Chop the 60-page document into individual pages
    pages = raw_contract_data.split("--- START OF PAGE")
    print(f"📋 Document split into {len(pages)} chunks for evaluation.")
    
    viable_chunks = []
    
    # Living Token FinOps Config Array
    # OLD BROAD KEYWORDS:
    # KEYWORDS = ["OTIF", "chargeback", "deduction", "penalty", "remedies", "compliance"]
    
    # NEW REFINED ENTERPRISE KEYWORDS:
    # We only look for explicit supply chain metrics and financial extractions
    KEYWORDS = ["OTIF", "chargeback deduction", "invoice valuation", "non-compliant shipments"]
    
    # 2. MAP PHASE: Scan pages locally at $0 token cost
    for index, page in enumerate(pages):
        minified_page = re.sub(r'\s+', ' ', page).strip()
        
        if any(word.lower() in minified_page.lower() for word in KEYWORDS):
            print(f"🎯 Token Gate Triggered: High-risk indicators found on Page Segment.")
            viable_chunks.append(minified_page)
            
    print(f"📊 FinOps Filtering Complete. Passed {len(viable_chunks)} chunks to LLM out of {len(pages)} original pages.")
    
    if not viable_chunks:
        print("✅ Clean Audit: No high-risk compliance clauses detected by Token Gate. Skipping LLM execution.")
        return
    
    optimized_payload = "\n".join(viable_chunks)
    
    print("\n--- Executing Stage 1 Extraction on Filtered Payload ---")
    extracted_data = extract_sla_metrics(optimized_payload)
    print("Stage 1 Output:", json.dumps(extracted_data, indent=2))

    print("\n--- Executing Stage 2 Risk Evaluation ---")
    audit_verdict = score_risk(extracted_data, legal_floor_pct=3.0)
    print("Stage 2 Final Verdict:", json.dumps(audit_verdict, indent=2))
    return audit_verdict

if __name__ == "__main__":
    print("🚀 Initializing Production Guarded Procurement Audit System...")
    
    # Target path to our newly generated 60-page contract
    file_path = "heavy_vendor_agreement.txt"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find {file_path}. Please run make_heavy_contract.py first.")
    else:
        print(f"📖 Loading un-audited document: {file_path} (~30,000 words)...")
        with open(file_path, "r") as f:
            raw_contract_data = f.read()
            
        print("⚡ Ingesting payload into the Token FinOps pipeline...")
        
        # Pass the massive 60-page text string straight into your audited engine!
        # Your custom code will automatically handle minification, filtering, and scoring.
        execute_audit_pipeline(raw_contract_data)
