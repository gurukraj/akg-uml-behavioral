#!/usr/bin/env python3
"""Materialize the AKG of one parsed UML diagram with the translation rules of Table 5.

Input is a diagram directory in the parsed-JSON format used in the evaluation
(interaction_*.json, activity_*.json, statemachine_*.json, _diagram_info.json).
The diagram type decides which rules apply. Every element receives an IRI in the akg:
namespace, an rdf:type triple, and akg:sourceDiagram (diagram-level provenance).

Implementation notes (data limits of the parsed files):
  * The parsed interaction files list the operands of combined fragments without their
    content, so the alt/opt rule of Table 5 cannot be applied; messages are treated as one
    sequence, and loop fragments are not unrolled (every message is counted once).
  * The activation of a synchronous call ends with its reply or, when no reply is
    modelled, with the finish of the execution specification started by the call.
  * The parsed files contain no timing-diagram elements, so no constraint triples arise.
"""
import json
import os
import re
from collections import defaultdict

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

AKG = Namespace("https://w3id.org/akg/behavioral#")
SEQ_NUM = re.compile(r"^\s*(\d+(?:\.\d+)*)\s*[:.]?\s")


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_\-]", "_", str(s))


class Builder:
    def __init__(self, diagram_id):
        self.g = Graph()
        self.g.bind("akg", AKG)
        self.did = diagram_id

    def iri(self, key):
        return AKG[f"{_safe(self.did)}__{_safe(key)}"]

    def node(self, key, cls, name=None):
        s = self.iri(key)
        self.g.add((s, RDF.type, AKG[cls]))
        self.g.add((s, AKG.sourceDiagram, Literal(self.did)))
        if name is not None:
            self.g.add((s, AKG.componentName, Literal(str(name))))
        return s

    def add(self, s, p, o):
        self.g.add((s, AKG[p], o))


def _files(diagram_dir, prefix):
    return [os.path.join(diagram_dir, f) for f in sorted(os.listdir(diagram_dir))
            if f.lower().startswith(prefix) and f.endswith(".json")]


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def interaction(b, data, communication=False):
    """Sequence rules of Table 5; with communication=True the communication rules."""
    life_cls = "CollaborationObject" if communication else "Lifeline"
    msg_cls = "CollaborationMessage" if communication else "Message"
    lifelines = {l["key"]: l for l in data.get("lifelines", [])}
    for k, l in lifelines.items():
        b.node(k, life_cls, l.get("name") or "")
    frags = data.get("fragments", [])
    pos = {f["key"]: i for i, f in enumerate(frags)}
    covered = {f["key"]: f.get("covered") for f in frags}
    msgs = data.get("messages", [])
    calls = [m for m in msgs if m.get("messageSort") != "reply"]
    by_send = {m.get("sendEvent"): m for m in msgs}
    by_recv = {m.get("receiveEvent"): m for m in msgs}
    exec_finish = {}  # finish occurrence -> start occurrence
    for f in frags:
        if f.get("type", "").endswith("ExecutionSpecification") and f.get("start") and f.get("finish"):
            exec_finish[f["finish"]] = f["start"]

    res = {}
    for m in calls:
        s = b.node(m["key"], msg_cls, m.get("name") or "")
        res[m["key"]] = s
        for ev, role in ((m.get("sendEvent"), "sender"), (m.get("receiveEvent"), "receiver")):
            ll = covered.get(ev)
            if ll in lifelines:
                b.add(s, "involves", b.iri(ll))
                b.add(s, role, b.iri(ll))
        if not communication:
            b.add(s, "isSync", Literal(m.get("messageSort") == "synchCall"))

    def order_key(m):
        return pos.get(m.get("sendEvent"), pos.get(m.get("receiveEvent"), 10 ** 9))

    numbered = {}
    if communication:
        for m in calls:
            mt = SEQ_NUM.match(m.get("name") or "")
            if mt:
                numbered[m["key"]] = mt.group(1)
                b.add(res[m["key"]], "sequenceNumber", Literal(mt.group(1)))
    if communication and numbered and len(numbered) == len(calls):
        ordered = sorted(calls, key=lambda m: [int(x) for x in numbered[m["key"]].split(".")])
        by_num = {v: k for k, v in numbered.items()}
        for m in calls:
            parent = numbered[m["key"]].rsplit(".", 1)[0] if "." in numbered[m["key"]] else None
            if parent in by_num:
                b.add(res[m["key"]], "causedBy", res[by_num[parent]])
    else:
        ordered = sorted(calls, key=order_key)
    for a, c in zip(ordered, ordered[1:]):
        b.add(res[a["key"]], "precedes", res[c["key"]])

    out = defaultdict(set)
    inn = defaultdict(set)
    for m in calls:
        snd, rcv = covered.get(m.get("sendEvent")), covered.get(m.get("receiveEvent"))
        if snd in lifelines and rcv in lifelines and snd != rcv:
            out[snd].add(rcv)
            inn[rcv].add(snd)
    if communication:
        for k in lifelines:
            b.add(b.iri(k), "fanIn", Literal(len(inn[k])))
            b.add(b.iri(k), "fanOut", Literal(len(out[k])))
        return

    # Nesting of calls (Table 5): parent = open synchronous call received by the sender of m
    stack = defaultdict(list)
    depth = {}
    for f in frags:
        k = f["key"]
        m = by_send.get(k)
        if m is not None:
            ll = covered.get(k)
            if m.get("messageSort") == "reply":
                if stack[ll]:
                    stack[ll].pop()
            elif m["key"] in res:
                parent = stack[ll][-1] if stack[ll] else None
                depth[m["key"]] = depth[parent["key"]] + 1 if parent else 1
                b.add(res[m["key"]], "callChainDepth", Literal(depth[m["key"]]))
                if parent is not None:
                    b.add(res[m["key"]], "causedBy", res[parent["key"]])
        if k in exec_finish:
            started = by_recv.get(exec_finish[k])
            ll = covered.get(exec_finish[k])
            if started is not None and started in stack[ll]:
                stack[ll].remove(started)
        m = by_recv.get(k)
        if m is not None and m.get("messageSort") == "synchCall" and m["key"] in res:
            stack[covered.get(k)].append(m)
    for m in calls:
        if m["key"] not in depth:
            b.add(res[m["key"]], "callChainDepth", Literal(1))


def activity(b, data):
    parts = {p["key"]: p for p in data.get("partitions", []) if isinstance(p, dict) and p.get("key")}
    for k, p in parts.items():
        b.node(k, "ActivityPartition", p.get("name") or "")
    nodes = {n["key"]: n for n in data.get("nodes", [])}
    outgoing = defaultdict(int)
    flows = [e for e in data.get("edges", []) if e.get("edgeType") == "uml:ControlFlow"]
    for e in flows:
        outgoing[e.get("source")] += 1
    for k, n in nodes.items():
        t = n.get("nodeType", "")
        if t in ("uml:OpaqueAction", "uml:CallBehaviorAction"):
            s = b.node(k, "Action", n.get("name") or "")
            part = n.get("inPartition")
            part = part[0] if isinstance(part, list) and part else part
            if part:
                if part not in parts:
                    b.node(part, "ActivityPartition", part)
                b.add(s, "belongsToPartition", b.iri(part))
        elif t == "uml:ForkNode":
            s = b.node(k, "ForkNode", n.get("name") or "")
            b.add(s, "fanOut", Literal(outgoing[k]))
        elif t == "uml:JoinNode":
            b.node(k, "JoinNode", n.get("name") or "")
        elif t == "uml:DecisionNode":
            b.node(k, "DecisionNode", n.get("name") or "")
        else:
            b.node(k, "BehavioralElement", n.get("name") or "")
    for e in flows:
        x, y = e.get("source"), e.get("target")
        b.node(e["key"], "ControlFlow", e.get("name") or "")
        if x in nodes and y in nodes:
            b.add(b.iri(x), "precedes", b.iri(y))
            b.add(b.iri(y), "causedBy", b.iri(x))


def statemachine(b, data):
    m = b.node(data.get("key", "sm"), "BehavioralElement", data.get("name") or "")
    n = 0
    for reg in data.get("regions", []):
        for st in reg.get("states", []):
            s = b.node(st["key"], "State", st.get("name") or "")
            if st.get("stateType") == "uml:State":
                n += 1
        for t in reg.get("transitions", []):
            s = b.node(t["key"], "Transition", t.get("name") or "")
            if t.get("source"):
                b.add(b.iri(t["source"]), "precedes", s)
            if t.get("target"):
                b.add(s, "precedes", b.iri(t["target"]))
            if t.get("guard") not in (None, "", "true"):
                gd = b.node(t["key"] + "_guard", "Guard", t["guard"])
                b.add(s, "hasGuard", gd)
            for trg in t.get("triggers", []) or []:
                ev = b.node(f"{t['key']}_{trg}", "Event", trg)
                b.add(ev, "triggers", s)
    b.add(m, "stateCount", Literal(n))


def materialize(diagram_id, diagram_dir, diagram_type):
    b = Builder(diagram_id)
    if diagram_type in ("Sequence", "Communication"):
        for f in _files(diagram_dir, "interaction"):
            d = _load(f)
            if d:
                interaction(b, d, communication=diagram_type == "Communication")
    elif diagram_type == "Activity":
        for f in _files(diagram_dir, "activity"):
            d = _load(f)
            if d:
                activity(b, d)
    elif diagram_type == "StateMachine":
        for f in _files(diagram_dir, "statemachine"):
            d = _load(f)
            if d:
                statemachine(b, d)
    return b.g
