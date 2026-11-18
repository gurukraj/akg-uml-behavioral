#!/usr/bin/env python3
"""Wilson 95% intervals for Tables 12-13 and results per classification group (primary / score-signal).

Input: results/per_diagram_results.json written by validate_behavioral_diagrams.py.
Output: results/intervals_and_groups.json
"""
import json
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
Z = 1.959964

DETECTORS = [
    ("Synchronous call chain", "Sequence", "SYNC_CALL_CHAIN", "patterns"),
    ("Hub component", "Communication", "HUB_COMPONENT", "patterns"),
    ("Workflow convergence", "Activity", "WORKFLOW_CONVERGENCE", "patterns"),
    ("Chatty interface", "Sequence", "CHATTY_INTERFACE", "smells"),
    ("State explosion", "StateMachine", "STATE_EXPLOSION", "smells"),
    ("Cyclic collaboration", "Communication", "CYCLIC_COLLABORATION_CANDIDATE", "smells"),
    ("God activity", "Activity", "GOD_ACTIVITY", "smells"),
]
TYPES = ["Activity", "Sequence", "StateMachine", "Communication", "Timing"]


def wilson(k, n):
    if n == 0:
        return None
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return [round(100 * max(0.0, c - h), 1), round(100 * min(1.0, c + h), 1)]


def confusion(rows, key, field):
    tp = sum(1 for r in rows if key in r[field] and key in r["gt_" + field])
    fp = sum(1 for r in rows if key in r[field] and key not in r["gt_" + field])
    fn = sum(1 for r in rows if key not in r[field] and key in r["gt_" + field])
    return tp, fp, fn, len(rows) - tp - fp - fn


def metrics(tp, fp, fn, tn):
    n = tp + fp + fn + tn
    return {
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "accuracy": round(100 * (tp + tn) / n, 1) if n else None, "accuracy_ci": wilson(tp + tn, n),
        "precision": round(100 * tp / (tp + fp), 1) if tp + fp else None, "precision_ci": wilson(tp, tp + fp),
        "recall": round(100 * tp / (tp + fn), 1) if tp + fn else None, "recall_ci": wilson(tp, tp + fn),
    }


def main():
    rows = json.load(open(os.path.join(RESULTS, "per_diagram_results.json")))
    out = {"composition": {}, "detectors": {}, "timing": {}, "validation_by_group": {}}
    for t in TYPES:
        out["composition"][t] = dict(Counter(r["group"] for r in rows if r["type"] == t))
    for name, dtype, key, field in DETECTORS:
        sel = [r for r in rows if r["type"] == dtype]
        out["detectors"][name] = {"all": metrics(*confusion(sel, key, field))}
        for g in ("primary", "score"):
            gs = [r for r in sel if r["group"] == g]
            out["detectors"][name][g] = metrics(*confusion(gs, key, field)) if gs else None
    tim = [r for r in rows if r["type"] == "Timing"]
    out["timing"] = {"n": len(tim), "flagged": sum(r["has_tc"] for r in tim),
                     "max_confidence": max((r["conf"] or 0) for r in tim)}
    for g in ("primary", "score"):
        for t in TYPES:
            gs = [r for r in rows if r["type"] == t and r["group"] == g]
            if gs:
                out["validation_by_group"][f"{g}/{t}"] = {
                    "n": len(gs), "structural": sum(r["L"][0] for r in gs), "completeness": sum(r["L"][1] for r in gs),
                    "semantic": sum(r["L"][2] for r in gs), "compatibility": sum(r["L"][3] for r in gs)}
    json.dump(out, open(os.path.join(RESULTS, "intervals_and_groups.json"), "w"), indent=1)
    for name, v in out["detectors"].items():
        a = v["all"]
        print(f"{name:24s} {a['TP']:>3} {a['FP']:>3} {a['FN']:>3} {a['TN']:>3}  acc {a['accuracy']} {a['accuracy_ci']}  "
              f"prec {a['precision']} {a['precision_ci']}  rec {a['recall']} {a['recall_ci']}")
    print("composition", out["composition"])


if __name__ == "__main__":
    main()
