"""Measure the free token gate on a small labeled set of contract clauses.

A clause is labeled True if it ties a delivery metric to a financial remedy,
which is what the gate should send to the model. This needs no API key.

    python evals/run_gate_eval.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contract_auditor import boolean_token_gate  # noqa: E402

cases = json.loads((ROOT / "evals" / "gate_cases.json").read_text())
tp = fp = fn = tn = 0
misses = []
for c in cases:
    pred = boolean_token_gate(c["text"])
    if pred and c["label"]:
        tp += 1
    elif pred and not c["label"]:
        fp += 1; misses.append(("false positive", c))
    elif not pred and c["label"]:
        fn += 1; misses.append(("false negative", c))
    else:
        tn += 1

precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
print(f"cases={len(cases)}  TP={tp} FP={fp} FN={fn} TN={tn}")
print(f"precision={precision:.0%}  recall={recall:.0%}")
for kind, c in misses:
    print(f"  {kind}: {c['id']} {c['text'][:90]}")
