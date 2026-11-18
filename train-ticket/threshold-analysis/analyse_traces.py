#!/usr/bin/env python3
"""
Analysis B: does the synchronous call-chain threshold (depth > T) separate slow endpoints?

For every endpoint of the workload, the Jaeger traces recorded during its time window are retrieved.
Runtime depth = number of services on the longest root-to-leaf path of the span tree (the entry service
counts as depth 1, as in Table 2). Server latency = duration of the root span. Units are endpoints.
"""
import json, statistics, sys
import numpy as np
import requests
from scipy.stats import mannwhitneyu, spearmanr

JAEGER = "http://localhost:16686"
THRESHOLDS = [1, 2, 3, 4, 5]


def traces(service, start_us, end_us):
    r = requests.get(f"{JAEGER}/api/traces", params={"service": service, "start": start_us, "end": end_us, "limit": 2000}, timeout=120)
    return r.json().get("data") or []


def analyse_trace(t):
    spans = {s["spanID"]: s for s in t["spans"]}
    svc = {s["spanID"]: t["processes"][s["processID"]]["serviceName"] for s in t["spans"]}
    children = {k: [] for k in spans}
    roots = []
    for s in t["spans"]:
        parents = [r["spanID"] for r in s.get("references", []) if r.get("refType") == "CHILD_OF" and r["spanID"] in spans]
        (children[parents[0]].append(s["spanID"]) if parents else roots.append(s["spanID"]))
    if not roots:
        return None
    root = min(roots, key=lambda k: spans[k]["startTime"])

    def depth(k, d, cur):
        best = d
        for c in children[k]:
            nd = d + (1 if svc[c] != cur else 0)
            best = max(best, depth(c, nd, svc[c]))
        return best
    services = set(svc.values())
    from collections import Counter
    pairs = Counter()
    for s_ in t["spans"]:
        for ref in s_.get("references", []):
            if ref.get("refType") == "CHILD_OF" and ref["spanID"] in svc and svc[ref["spanID"]] != svc[s_["spanID"]]:
                pairs[frozenset((svc[ref["spanID"]], svc[s_["spanID"]]))] += 1
    max_pair = max(pairs.values()) if pairs else 0
    server_spans = sum(1 for s in t["spans"] if any(tag.get("key") == "span.kind" and tag.get("value") == "server" for tag in s.get("tags", [])))
    return {"root_service": svc[root], "depth": depth(root, 1, svc[root]), "duration_ms": spans[root]["duration"] / 1000,
            "distinct_services": len(services), "spans": len(t["spans"]), "max_calls_per_pair": max_pair, "server_spans": server_spans}


def a12(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if not len(x) or not len(y):
        return None
    return float(sum((xi > y).sum() + 0.5 * (xi == y).sum() for xi in x) / (len(x) * len(y)))


def main():
    wl = json.load(open("workload_results.json"))
    static = {(e["service"], e["verb"], e["path"]): e for e in json.load(open("endpoints_static_v1.json"))}
    units = []
    for e in wl:
        ok = sum(1 for c in e["http_status"] if c == 200) / len(e["http_status"])
        ts = [analyse_trace(t) for t in traces(e["service"], e["start_us"], e["end_us"])]
        ts = [x for x in ts if x and x["root_service"] == e["service"]]
        unit = {"service": e["service"], "method": e["method"], "path": e["path"], "success_rate": ok, "traces": len(ts),
                "client_median_ms": statistics.median(e["latencies_ms"])}
        if ts:
            unit.update({"runtime_depth": max(x["depth"] for x in ts),
                         "server_median_ms": statistics.median(x["duration_ms"] for x in ts),
                         "distinct_services": max(x["distinct_services"] for x in ts),
                         "server_spans": statistics.median(x["server_spans"] for x in ts),
                         "max_calls_per_pair": statistics.median(x["max_calls_per_pair"] for x in ts)})
        units.append(unit)
    valid = [u for u in units if u["success_rate"] >= 0.8 and u.get("traces", 0) >= 5]
    depth = np.array([u["runtime_depth"] for u in valid])
    lat = np.array([u["server_median_ms"] for u in valid])
    calls = np.array([u["server_spans"] for u in valid])
    slow = lat > np.median(lat)
    rows = []
    for T in THRESHOLDS:
        flag = depth > T
        f, n = lat[flag], lat[~flag]
        p = float(mannwhitneyu(f, n, alternative="greater").pvalue) if len(f) >= 2 and len(n) >= 2 else None
        tpr = float((flag & slow).sum() / slow.sum()) if slow.sum() else None
        fpr = float((flag & ~slow).sum() / (~slow).sum()) if (~slow).sum() else None
        rows.append({"T": T, "flagged": int(flag.sum()), "median_latency_flagged": float(np.median(f)) if len(f) else None,
                     "median_latency_not_flagged": float(np.median(n)) if len(n) else None, "A12": a12(f, n), "p_mannwhitney": p,
                     "precision_slow": float((flag & slow).sum() / flag.sum()) if flag.sum() else None, "recall_slow": tpr,
                     "youden_J": (tpr - fpr) if tpr is not None and fpr is not None else None})
    rho_d, p_d = spearmanr(depth, lat); rho_c, p_c = spearmanr(calls, lat); rho_dc, _ = spearmanr(depth, calls)
    # static vs runtime depth agreement (for endpoints present in the static catalogue)
    agree = []
    for u in valid:
        key = next((k for k in static if k[0] == u["service"] and k[1] == u["method"] and
                    __import__("re").fullmatch(__import__("re").sub(r"\\\{[^}]*\\\}", "[^/]+", __import__("re").escape(k[2])), u["path"])), None)
        if key:
            agree.append((static[key]["static_depth"], u["runtime_depth"]))
    out = {"endpoints_called": len(units), "endpoints_valid": len(valid), "latency_median_ms": float(np.median(lat)),
           "depth_distribution": {int(k): int((depth == k).sum()) for k in sorted(set(depth))},
           "spearman_depth_latency": {"rho": float(rho_d), "p": float(p_d)},
           "spearman_calls_latency": {"rho": float(rho_c), "p": float(p_c)},
           "spearman_depth_calls": float(rho_dc),
           "auc_depth_for_slow": a12(depth[slow], depth[~slow]),
           "youden_best_T": max(rows, key=lambda r: r["youden_J"] if r["youden_J"] is not None else -9)["T"],
           "thresholds": rows,
           "static_vs_runtime_depth": {"pairs": len(agree), "exact_agreement": sum(1 for a, b in agree if a == b),
                                       "static_greater": sum(1 for a, b in agree if a > b), "static_smaller": sum(1 for a, b in agree if a < b)},
           "units": units}
    from scipy.stats import rankdata, t as tdist
    def partial(x, y, z):
        rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
        res = lambda a, b: a - np.polyval(np.polyfit(b, a, 1), b)
        r = float(np.corrcoef(res(rx, rz), res(ry, rz))[0, 1]); n = len(x)
        return {"rho": r, "p": float(2 * (1 - tdist.cdf(abs(r * np.sqrt((n - 3) / (1 - r * r))), n - 3)))}
    out["partial_spearman_depth_latency_given_calls"] = partial(depth, lat, calls)
    out["median_latency_by_depth"] = {int(k): float(np.median(lat[depth == k])) for k in sorted(set(depth))}
    budgets = {}
    for budget in (100, 200):
        slow_b = lat > budget
        budgets[budget] = []
        for T in THRESHOLDS:
            flag = depth > T
            tpr = float((flag & slow_b).sum() / slow_b.sum()) if slow_b.sum() else None
            fpr = float((flag & ~slow_b).sum() / (~slow_b).sum()) if (~slow_b).sum() else None
            budgets[budget].append({"T": T, "precision": float((flag & slow_b).sum() / flag.sum()) if flag.sum() else None,
                                    "recall": tpr, "youden_J": (tpr - fpr) if tpr is not None and fpr is not None else None})
    out["latency_budget_analysis"] = {str(k): {"slow_endpoints": int((lat > k).sum()), "auc": a12(depth[lat > k], depth[lat <= k]),
                                               "best_T": max(v, key=lambda r: r["youden_J"] if r["youden_J"] is not None else -9)["T"], "thresholds": v}
                                      for k, v in budgets.items()}
    chat = np.array([u["max_calls_per_pair"] for u in valid])
    crow = []
    slow100 = lat > 100
    for T in [2, 3, 4, 5, 6, 7, 8, 10, 15, 20]:
        flag = chat > T
        f, n = lat[flag], lat[~flag]
        tpr = float((flag & slow100).sum() / slow100.sum()) if slow100.sum() else None
        fpr = float((flag & ~slow100).sum() / (~slow100).sum())
        crow.append({"T": T, "flagged": int(flag.sum()), "median_latency_flagged": float(np.median(f)) if len(f) else None,
                     "median_latency_not_flagged": float(np.median(n)) if len(n) else None, "A12": a12(f, n),
                     "p_mannwhitney": float(mannwhitneyu(f, n, alternative="greater").pvalue) if len(f) >= 2 and len(n) >= 2 else None,
                     "precision_100ms": float((flag & slow100).sum() / flag.sum()) if flag.sum() else None, "recall_100ms": tpr,
                     "youden_J_100ms": (tpr - fpr) if tpr is not None else None})
    rc, pc = spearmanr(chat, lat)
    out["chatty"] = {"distribution": {float(k): int((chat == k).sum()) for k in sorted(set(chat))},
                     "spearman_maxpair_latency": {"rho": float(rc), "p": float(pc)},
                     "spearman_maxpair_calls": float(spearmanr(chat, calls)[0]),
                     "partial_maxpair_latency_given_calls": partial(chat, lat, calls),
                     "best_T_100ms": max(crow, key=lambda r: r["youden_J_100ms"] if r["youden_J_100ms"] is not None else -9)["T"],
                     "thresholds": crow}
    json.dump(out, open("b_results.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1))


if __name__ == "__main__":
    main()
