"""Offline tests: the model is replaced by a stub, so no API key is needed."""
import json
from pathlib import Path

import pytest

import contract_auditor as ca

ROOT = Path(__file__).resolve().parent.parent


def fake_llm(penalty):
    def _llm(clause):
        content = json.dumps({"metric_pct": "98%", "trigger_window": "two quarters", "penalty_pct": penalty})
        return {"choices": [{"message": {"content": content}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}}
    return _llm


# ---------- token gate ----------
def test_gate_needs_metric_and_remedy():
    assert ca.boolean_token_gate("OTIF below 98% triggers a 3% penalty")
    assert not ca.boolean_token_gate("OTIF is reported monthly")            # metric only
    assert not ca.boolean_token_gate("Force majeure suspends obligations without penalty")  # remedy only


def test_gate_catches_defensive_vocabulary():
    assert ca.boolean_token_gate("Buyer may assess a chargeback on non-compliant shipments")
    assert ca.boolean_token_gate("Amounts for late shipments may be offset against invoices")


# ---------- percent parsing ----------
@pytest.mark.parametrize("raw,expected", [
    (3, 3.0), ("3%", 3.0), ("1.5 percent", 1.5),
    ("3% of gross invoice value", 3.0), ("none", None), (None, None),
])
def test_parse_percent(raw, expected):
    assert ca.parse_percent(raw) == expected


# ---------- rules ----------
def test_penalty_below_floor_is_flagged():
    r = ca.score_risk({"status": "SUCCESS", "penalty_pct": "1.5%"})
    assert r["risk_score"] == "CRITICAL_FLAG"


def test_penalty_at_floor_passes():
    r = ca.score_risk({"status": "SUCCESS", "penalty_pct": "3% of gross value"})
    assert r["risk_score"] == "COMPLIANT_PASS"


def test_failed_extraction_is_unknown():
    assert ca.score_risk({"status": "ERROR"})["risk_score"] == "UNKNOWN"


# ---------- extraction ----------
def test_schema_validation_rejects_missing_keys():
    bad = lambda clause: {"choices": [{"message": {"content": '{"metric_pct": "98%"}'}}]}
    out = ca.extract_sla_metrics("OTIF 98%, 3% penalty", llm=bad)
    assert out["status"] == "SCHEMA_ERROR"


def test_missing_key_is_a_clear_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        ca.extract_sla_metrics("OTIF 98%, 3% penalty")


# ---------- end to end on the sample contract ----------
SAMPLE = (ROOT / "heavy_vendor_agreement.txt").read_text()


def test_sample_contract_gate_keeps_only_the_sla_page():
    result = ca.execute_audit_pipeline(SAMPLE, dry_run=True)
    assert result["pages"] == 60 and result["gated_pages"] == [42]


def test_sample_contract_weak_penalty_is_flagged():
    result = ca.execute_audit_pipeline(SAMPLE, llm=fake_llm("1.5%"))
    assert result["verdict"] == "CRITICAL_FLAG"
    assert result["findings"][0]["page"] == 42
