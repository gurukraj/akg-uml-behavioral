# AKG for UML behavioral models: ontology, code, and data

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24347428.svg)](https://doi.org/10.5281/zenodo.24347428)

Replication package for the article

> G. Kulkarni, C. S. Lamba, and S. Solanki, "Architectural Knowledge Graphs from UML Behavioural Models for Early Architectural Bottleneck and Smell Detection," *Discover Artificial Intelligence* (under review).

It contains the AKG ontology, the extraction, sampling, reference-label, and detection code of the evaluation, the code that materializes the AKG and executes the SPARQL queries, the Train-Ticket models, and the result files behind the tables.

## Contents

| Folder / file | Content | Article |
|---|---|---|
| `ontology/akg-behavioral.ttl` | AKG ontology (RDFS, Turtle), namespace `https://w3id.org/akg/behavioral#`, CC BY 4.0 | Table 4 |
| `extraction/4_extract_all_uml_information.py` | Extraction of all UML element types from the GenMyModel XMI files into per-diagram JSON files | Sections 3.3, 6.1 |
| `extraction/classify_uml_enhanced_v3.py` | Heuristic classification of the diagram type (scores per type) | Section 6.1 |
| `evaluation/validate_behavioral_diagrams.py` | Sampling (seed 42), validation checks, semantic extraction, detection rules, reference labels (`GroundTruthEstablisher`), metrics | Sections 6.2–6.5, Tables 8–13 |
| `evaluation/validate_behavioral_diagrams_original.py` | The script as run for the first submission (see "Determinism" below) | – |
| `evaluation/behavioral_index_39220.json.gz` | Index of the 39,220 behavioral diagrams (7,391 primary-classified, 31,829 score-signal-classified): identifiers, file names, classification scores | Section 6.1 |
| `evaluation/intervals_and_groups.py` | Wilson 95% intervals and results per classification group | Tables 12–13, Section 6.2 |
| `evaluation/results/` | `per_diagram_results.json` (the 428 sampled diagrams with group, checks, extraction, detections, reference labels), `validation_results.json`, `intervals_and_groups.json` | Tables 8–13 |
| `akg/materialize.py` | AKG construction with the translation rules of Table 5 | Section 3.6, Table 5 |
| `akg/queries/Q1…Q8*.rq` | The eight SPARQL queries of Section 5; `published/` holds the cyclic-collaboration query of the previous version | Section 5 |
| `akg/run_queries.py`, `akg/check_examples.py` | Materialization of the 428 diagrams and the Train-Ticket models, query execution on Apache Jena Fuseki and rdflib, comparison with the rules; query check on the examples of Section 4 | Section 7.6 |
| `akg/results/` | `query_results.json`, `example_checks.json`, `graphs/*.trig` (all graphs) | Section 7.6 |
| `train-ticket/` | Train-Ticket UML models, their generator, threshold analysis (Section 7.5), refactoring validation (Section 5.9); see `train-ticket/README.md` | Sections 5.9, 7.5 |
| `w3id/` | Redirect rules for the persistent namespace | – |

## Reproduction

Requirements: Python 3.10, `rdflib` 7.6, `numpy`, `scipy`; Java 17 and Apache Jena Fuseki 5.4 for the query run.

1. GenMyModel data. The XMI crawl is part of the repository of Baumgartner, *UML Class Diagram Dataset* (https://github.com/NilsBaumgartner1994/UML-Class-Diagram-Dataset). The models are not redistributed here. Extract the per-diagram JSON files with
   `python extraction/4_extract_all_uml_information.py extract-xmi <xmi folder> --output_folder 4_Extracted-All-UML-Informations`.
2. Evaluation (Tables 8–13):
   `AKG_DATASET_DIR=<…>/4_Extracted-All-UML-Informations python evaluation/validate_behavioral_diagrams.py`, then `python evaluation/intervals_and_groups.py`.
3. AKG and SPARQL queries:
   `fuseki-server --mem --port 3399 /akg &`, then `AKG_DATASET_DIR=<…> python akg/run_queries.py` and `python akg/check_examples.py`.

## Determinism

The script of the first submission assigned a score-signal diagram with equal top scores to the type that came first in the iteration order of a Python `set`, and it read the files of a diagram in the iteration order of a `set` and of `os.listdir`. Both orders can change between runs (string-hash randomization, file system). The current script fixes the priority Sequence > Communication > State machine > Timing > Activity for equal scores and reads files in lexicographic order. With these rules, it reproduces the published strata (21,464 / 5,402 / 11,565 / 761 / 28), the same 428 diagrams, and Tables 8–13 exactly, for any value of `PYTHONHASHSEED`. The only cell that depended on the order was one communication diagram with two interaction files (hub rule).

## Licenses

Code: Apache License 2.0 (`LICENSE`). Ontology, documentation, models, and result files: CC BY 4.0 (`LICENSE-CC-BY-4.0.md`). The Train-Ticket system (FudanSELab) is licensed under Apache 2.0. The element names in `akg/results/graphs/genmymodel_428.trig` and the file names in `evaluation/behavioral_index_39220.json.gz` come from the public GenMyModel models of [Baumgartner's dataset](https://github.com/NilsBaumgartner1994/UML-Class-Diagram-Dataset) and remain subject to its terms.

## Citation

Archived at Zenodo: https://doi.org/10.5281/zenodo.24347428. See `CITATION.cff`.
