#!/usr/bin/env python3
"""Execute the queries of Section 5 on small graphs built from the illustrative triples of Sections 4.2, 4.3 and 4.5.

The sample contains no positive case for timing violation, state explosion, and god activity; these
examples check that the three queries are syntactically valid and return the expected rows.
Runs on Apache Jena Fuseki (AKG_FUSEKI, in-memory dataset), because rdflib cannot compare xsd:duration values.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_queries import QUERIES, fuseki_load, fuseki_query  # noqa: E402
from rdflib import Graph  # noqa: E402

P = ("@prefix akg: <https://w3id.org/akg/behavioral#> . @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . "
     "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
EXAMPLES = {
    # Section 4.5: a 2 s duration bound on PaymentService, which takes part in a call at depth 4
    "Q4": (P + """akg:PaymentProcessingConstraint rdf:type akg:DurationConstraint ; akg:componentName "PaymentProcessing" ;
    akg:timingBound "PT2S"^^xsd:duration ; akg:involves akg:PaymentService .
akg:OrderConfirmationConstraint rdf:type akg:TimeConstraint ; akg:componentName "OrderConfirmation" ;
    akg:timingBound "PT5S"^^xsd:duration ; akg:involves akg:OrderService .
akg:PaymentService akg:componentName "PaymentService" . akg:OrderService akg:componentName "OrderService" .
akg:m4 rdf:type akg:Message ; akg:isSync true ; akg:involves akg:OrderService , akg:PaymentService ; akg:callChainDepth 4 .""", 1),
    # Section 4.2: the order state machine, once with 2 and once with 16 states
    "Q6": (P + """akg:OrderLifecycle rdf:type akg:BehavioralElement ; akg:componentName "OrderLifecycle" ; akg:stateCount 2 .
akg:LargeLifecycle rdf:type akg:BehavioralElement ; akg:componentName "LargeLifecycle" ; akg:stateCount 16 .""", 1),
    # Section 4.3: four actions, three of them in OrderService (75% > 40%)
    "Q8": (P + """akg:OrderServicePartition akg:componentName "OrderService" . akg:PaymentServicePartition akg:componentName "PaymentService" .
akg:ProcessOrderAction rdf:type akg:Action ; akg:belongsToPartition akg:OrderServicePartition .
akg:ValidateOrderAction rdf:type akg:Action ; akg:belongsToPartition akg:OrderServicePartition .
akg:ConfirmOrderAction rdf:type akg:Action ; akg:belongsToPartition akg:OrderServicePartition .
akg:ProcessPaymentAction rdf:type akg:Action ; akg:belongsToPartition akg:PaymentServicePartition .""", 1),
}


def main():
    out = {}
    for q, (ttl, expected) in EXAMPLES.items():
        g = Graph().parse(data=ttl, format="turtle")
        fuseki_load(g.serialize(format="nt"))
        rows = fuseki_query(QUERIES[q])
        out[q] = {"rows": rows, "expected_rows": expected, "ok": len(rows) == expected}
        print(q, out[q])
    json.dump(out, open(os.path.join(HERE, "results", "example_checks.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
