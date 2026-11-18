#!/usr/bin/env python3
"""R11: materialize the AKG per diagram, execute the SPARQL queries of Section 5, compare with the rules.

Every diagram graph is loaded into Apache Jena Fuseki (in-memory dataset) and queried over HTTP;
the same queries are executed with rdflib as a cross-check (rdflib does not compare xsd:duration
values, so Q4 can only be evaluated by Jena).

Usage:
  fuseki-server --mem --port 3399 /akg &            # Apache Jena Fuseki 5.4.0
  AKG_DATASET_DIR=<GenMyModel 4_Extracted-All-UML-Informations> \
  AKG_TT_DIR=<processed Train-Ticket models> python run_queries.py
Inputs : ../evaluation/results/per_diagram_results.json (rule results of the 428 sampled diagrams)
Outputs: results/query_results.json, results/graphs/<set>.trig (all graphs as named graphs)
"""
import glob
import json
import os
import statistics
import sys
import time
import urllib.parse
import urllib.request

from rdflib import Dataset, URIRef

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from materialize import materialize  # noqa: E402

DATASET_DIR = os.environ.get("AKG_DATASET_DIR", "4_Extracted-All-UML-Informations")
TT_DIR = os.environ.get("AKG_TT_DIR", os.path.join(HERE, "..", "train-ticket", "models-processed"))
FUSEKI = os.environ.get("AKG_FUSEKI", "http://localhost:3399/akg")
OUT = os.path.join(HERE, "results")
QUERIES = {os.path.basename(p)[:2]: open(p).read() for p in sorted(glob.glob(os.path.join(HERE, "queries", "Q*.rq")))}
QUERIES["Q7p"] = open(os.path.join(HERE, "queries", "published", "Q7_cyclic_collaboration_published.rq")).read()
RULES = {"Q1": ("Sequence", "SYNC_CALL_CHAIN", "patterns"), "Q2": ("Communication", "HUB_COMPONENT", "patterns"),
         "Q3": ("Activity", "WORKFLOW_CONVERGENCE", "patterns"), "Q4": ("Timing", None, None),
         "Q5": ("Sequence", "CHATTY_INTERFACE", "smells"), "Q6": ("StateMachine", "STATE_EXPLOSION", "smells"),
         "Q7": ("Communication", "CYCLIC_COLLABORATION_CANDIDATE", "smells"),
         "Q7p": ("Communication", "CYCLIC_COLLABORATION_CANDIDATE", "smells"), "Q8": ("Activity", "GOD_ACTIVITY", "smells")}
BEHAVIORAL = {"Sequence", "Activity", "StateMachine", "Communication", "Timing"}


def http(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def fuseki_load(nt):
    http(FUSEKI + "/data?default", data=nt.encode("utf-8"), headers={"Content-Type": "application/n-triples"}, method="PUT")


def fuseki_query(q):
    body = urllib.parse.urlencode({"query": q}).encode()
    res = json.loads(http(FUSEKI + "/query", data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/sparql-results+json"}))
    return [[b[v]["value"] if v in b else "" for v in res["head"]["vars"]] for b in res["results"]["bindings"]]


def run_set(name, items):
    ds = Dataset()
    rows, sizes = [], []
    qtime = {e: {q: 0.0 for q in QUERIES} for e in ("jena", "rdflib")}
    t_build = t_load = 0.0
    for did, ddir, dtype, rule in items:
        t0 = time.perf_counter()
        g = materialize(did, ddir, dtype)
        t_build += time.perf_counter() - t0
        sizes.append(len(g))
        ng = ds.graph(URIRef(f"urn:akg:diagram:{did}"))
        for t in g:
            ng.add(t)
        t0 = time.perf_counter()
        fuseki_load(g.serialize(format="nt"))
        t_load += time.perf_counter() - t0
        rec = {"id": did, "type": dtype, "triples": len(g), "jena": {}, "rdflib": {}, "rule": rule}
        for q, text in QUERIES.items():
            t0 = time.perf_counter()
            rec["jena"][q] = fuseki_query(text)
            qtime["jena"][q] += time.perf_counter() - t0
            t0 = time.perf_counter()
            rec["rdflib"][q] = [[str(x) for x in r] for r in g.query(text)]
            qtime["rdflib"][q] += time.perf_counter() - t0
        rows.append(rec)
    os.makedirs(os.path.join(OUT, "graphs"), exist_ok=True)
    ds.serialize(os.path.join(OUT, "graphs", f"{name}.trig"), format="trig")
    nonempty = [s for s in sizes if s]
    summary = {"diagrams": len(items), "nonempty_graphs": len(nonempty), "triples_total": sum(sizes),
               "triples_median_nonempty": statistics.median(nonempty) if nonempty else 0,
               "triples_max": max(sizes) if sizes else 0, "build_seconds": round(t_build, 2),
               "jena_load_seconds": round(t_load, 2),
               "query_seconds": {e: {q: round(v, 3) for q, v in d.items()} for e, d in qtime.items()},
               "query_seconds_total": {e: round(sum(d.values()), 2) for e, d in qtime.items()},
               "engine_row_count_mismatches": [(r["id"], q) for r in rows for q in QUERIES
                                               if len(r["jena"][q]) != len(r["rdflib"][q])]}
    return rows, summary


def compare(rows):
    out = {}
    for q, (dtype, key, field) in RULES.items():
        sel = [r for r in rows if r["type"] == dtype]
        qf = {r["id"] for r in sel if r["jena"][q]}
        if key is None:
            rf = {r["id"] for r in sel if r["rule"]["has_tc"]}
            ref = set()
        else:
            rf = {r["id"] for r in sel if key in r["rule"][field]}
            ref = {r["id"] for r in sel if key in r["rule"]["gt_" + field]}
        out[q] = {"type": dtype, "n": len(sel), "rule_flagged": len(rf), "query_flagged": len(qf),
                  "both": len(rf & qf), "rule_only": len(rf - qf), "query_only": len(qf - rf),
                  "reference_positive": len(ref),
                  "query_vs_reference": {"TP": len(qf & ref), "FP": len(qf - ref), "FN": len(ref - qf),
                                         "TN": len(sel) - len(qf | ref)},
                  "query_only_ids": sorted(qf - rf), "rule_only_ids": sorted(rf - qf)}
    return out


def main():
    rules = json.load(open(os.path.join(HERE, "..", "evaluation", "results", "per_diagram_results.json")))
    items = [(r["id"], os.path.join(DATASET_DIR, r["id"]), r["type"], r) for r in rules]
    g_rows, g_sum = run_set("genmymodel_428", items)
    idx = json.load(open(os.path.join(TT_DIR, "behavioral_index.json")))
    tt = [(os.path.basename(d["diagram_dir"]), os.path.join(TT_DIR, os.path.basename(d["diagram_dir"])), d["uml"]["type"], None)
          for k in ("primary_behavioral_diagrams", "score_signal_behavioral_diagrams") for d in idx.get(k, [])
          if d["uml"]["type"] in BEHAVIORAL]
    t_rows, t_sum = run_set("train_ticket", tt)
    res = {"engines": {"jena": "Apache Jena Fuseki 5.4.0 (in-memory)", "rdflib": "rdflib 7.6.0"},
           "genmymodel": {"summary": g_sum, "comparison": compare(g_rows), "diagrams": g_rows},
           "train_ticket": {"summary": t_sum, "diagrams": t_rows}}
    json.dump(res, open(os.path.join(OUT, "query_results.json"), "w"), indent=1)
    print("GenMyModel", json.dumps(g_sum))
    for q, c in res["genmymodel"]["comparison"].items():
        print(q, {k: v for k, v in c.items() if not k.endswith("_ids")})
    print("Train-Ticket", json.dumps(t_sum))
    for r in t_rows:
        print(" ", r["id"], r["type"], r["triples"], {q: len(v) for q, v in r["jena"].items() if v})


if __name__ == "__main__":
    main()
