# Train-Ticket models and analyses (Sections 5.9 and 7.5)

## Provenance of the UML models

| | Train-Ticket | Train-Ticket fork |
|---|---|---|
| Code base | FudanSELab/train-ticket, commit `313886e99befb94be6cd45f085c98e0019f59829` (1 Nov 2022) | Cambio-Project/trainticket-fork, commit `d24c84c1f0c59a7ce1f6faa9171575d243a0e947` (20 May 2021) |
| Models | `models-raw/` (29 diagrams: 8 sequence, 3 communication, 2 activity, 15 class, 1 component) | `fork/models-raw/` |
| Generator | `generate_uml_dataset.py` | `fork/generate_uml_dataset.py` |

The models were produced by the authors, not taken from existing work. Their content was derived from the source code with AI assistance: the services, endpoints, and the remote calls of each scenario were read from the controller and service classes (static reading of the code; no runtime traces). The result was encoded as fixed data in a generator script that writes the models in the GenMyModel-compatible JSON format, and the authors checked it against the source code. The order and the nesting of the calls in the sequence diagrams follow the call structure of the code; conditional branches were not evaluated. The models therefore describe the implemented system (a reverse-engineered design), not a design-time model.

The code-level check of Section 5.9 showed that the models omit calls: the static call tree of the reservation contains seven chains of depth 4, of which the sequence diagram shows one (`refactoring-validation/original_callgraph.txt`).

`prepare_trainticket_dataset.py` converts `models-raw/` into the format of the evaluation (`models-processed/`); the communication diagrams are converted into interactions, and execution specifications are added from the order of calls and replies:

    python prepare_trainticket_dataset.py --source models-raw --output models-processed --project-name Train-Ticket

## Threshold analysis (Section 7.5, Table 14, Figure 8)

`threshold-analysis/`: Train-Ticket release with distributed tracing (Docker images `codewisdom/ts-*-with-jaeger:v1`, `images.txt`, `compose-runtime.yml`) on one host; `workload.py` calls 53 endpoints, 30 times each after five warm-up requests, and retrieves the Jaeger traces; `analyse_traces.py` computes runtime call depth, the largest number of calls per pair of services, latency, Spearman correlations, Mann–Whitney U, Vargha–Delaney A12, and Youden's index (`b_results.json`, `b_results_summary.txt`). The user names and passwords in `workload.py` are the public demo accounts of Train-Ticket.

## Refactoring validation (Section 5.9, Table 7)

`refactoring-validation/`: `refactoring.patch` (against the code base above), `ReservationHarness.java` (executes the original and the refactored service classes with stand-ins for HTTP and the message broker), static call trees (`static_callgraph.py`, `*_callgraph.*`), and results (`harness_*.json`, `validation_summary.json`; 50 ms per synchronous call: 588 ms → 456 ms).
