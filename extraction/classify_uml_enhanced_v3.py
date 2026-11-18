#!/usr/bin/env python3
"""
classify_uml_enhanced_v3.py

Enhancements in this version:
  - Group JSONs by diagram UUID found under --extracted-json-root (authoritative)
  - Optional reconciliation with --root (purely informational)
  - NEW: Classify the UML diagram type per diagram_id using heuristics
        * Supports Structural vs Behavioral categories
        * Specific types: Class, Component, Deployment, Package, CompositeStructure, Object,
          UseCase, Activity, StateMachine, Sequence, Communication, InteractionOverview,
          Timing, Profile, Unknown
        * Basis can be 'filenames', 'content', or 'both'
        * Lightweight JSON inspection when requested

Usage examples:
  # Fast grouping + filename-based classification (default)
  python classify_uml_enhanced_v3.py \
    --extracted-json-root /path/to/3_Extracted-Class-Informations \
    --out-json UMLClass_Diagram_Classification_Extraction_New.json

  # Use JSON content to classify (slower), limit to first 100 files per diagram
  python classify_uml_enhanced_v3.py \
    --extracted-json-root /path/to/3_Extracted-Class-Informations \
    --classify-using content \
    --max-files-per-diagram 100 \
    --out-json UMLClass_Diagram_Classification_Extraction_New.json

  # Reconcile with --root (optional) and emit verbose signals that drove classification
  python classify_uml_enhanced_v3.py \
    --root /path/to/2_UML-Class-Diagrams \
    --extracted-json-root /path/to/3_Extracted-Class-Informations \
    --classify-using both \
    --emit-signals \
    --out-json UMLClass_Diagram_Classification_Extraction_New.json

"""

from __future__ import annotations
import argparse
import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Iterable, Any, Optional

# --- UUID detection (tolerant) -------------------------------------------------
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def extract_uuids(text: str | None) -> List[str]:
    """Return list of lowercase UUIDs found in text (may be empty)."""
    if not text:
        return []
    return [m.group(0).lower() for m in UUID_RE.finditer(text)]


# --- Filesystem helpers --------------------------------------------------------

def list_immediate_subdirs(root: str) -> List[str]:
    try:
        return [e.path for e in os.scandir(root) if e.is_dir()]
    except FileNotFoundError:
        return []


def list_json_files_nonrecursive(dir_path: str) -> List[str]:
    hits: List[str] = []
    try:
        for e in os.scandir(dir_path):
            if e.is_file() and e.name.lower().endswith(".json"):
                hits.append(e.path)
    except FileNotFoundError:
        pass
    return hits


def list_json_files_recursive(dir_path: str) -> List[str]:
    hits: List[str] = []
    for dp, _, fns in os.walk(dir_path):
        for fn in fns:
            if fn.lower().endswith(".json"):
                hits.append(os.path.join(dp, fn))
    return hits


def safe_load_json(path: str) -> Tuple[bool, Optional[Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return True, json.load(f)
    except Exception:
        return False, None


def safe_validate_json(path: str) -> Tuple[bool, str | None]:
    """Attempt to parse JSON file without keeping content.
    Returns (ok, error_message_or_None).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
        return True, None
    except Exception as e:
        return False, str(e)


# --- UML type classification ---------------------------------------------------
# Specific UML types and their keyword signals (both for filenames and content)
UML_TYPES: Dict[str, List[str]] = {
    # Structural
    "Class": [
        "class", "interface", "association", "generalization", "realization",
        "attribute", "operation", "classifier"],
    "Component": [
        "component", "port", "connector", "providedinterface", "requiredinterface",
        "assemblyconnector"],
    "Deployment": [
        "deployment", "node", "artifact", "device", "executionenvironment",
        "communicationpath"],
    "Package": [
        "package", "packagedelement", "packageimport", "packagemerge"],
    "CompositeStructure": [
        "composite", "collaboration", "part", "role", "structuredclassifier"],
    "Object": [
        "object", "slot", "instance", "instancespecification", "link", "objectdiagram"],

    # Behavioral
    "UseCase": [
        "usecase", "actor", "include", "extend", "usecasediagram"],
    "Activity": [
        "activity", "action", "controlflow", "objectflow", "activitynode",
        "pin", "activityfinal", "decisionnode", "forknode", "joinnode", "initialnode"],
    "StateMachine": [
        "statemachine", "state", "transition", "pseudostate", "finalstate",
        "region", "entry", "exit", "doactivity"],
    "Sequence": [
        "sequence", "lifeline", "message", "interaction", "combinedfragment",
        "fragment", "interactionoperand", "occurrencespecification"],
    "Communication": [
        "communication", "collaboration", "message", "link", "role"],
    "InteractionOverview": [
        "interactionoverview"],
    "Timing": [
        "timing", "timespecification", "timeslot", "lifeline"],
    "Profile": [
        "profile", "stereotype", "metaclass", "extension", "profileapplication"],
}

STRUCTURAL = {
    "Class", "Component", "Deployment", "Package", "CompositeStructure", "Object"
}
BEHAVIORAL = {
    "UseCase", "Activity", "StateMachine", "Sequence", "Communication",
    "InteractionOverview", "Timing"
}

# Precedence when scores tie (more common diagrams first)
TYPE_PRECEDENCE = [
    "Class", "Sequence", "Activity", "StateMachine", "UseCase",
    "Component", "Deployment", "Package", "CompositeStructure", "Object",
    "Communication", "InteractionOverview", "Timing", "Profile"
]


def diagram_category(uml_type: str) -> str:
    if uml_type in STRUCTURAL:
        return "Structural"
    if uml_type in BEHAVIORAL:
        return "Behavioral"
    if uml_type == "Profile":
        return "Structural"  # profiles extend structure
    return "Unknown"


SIGNAL_KEYS = {
    # keys in JSON we will look at for quick hints (shallow)
    "type", "umlType", "uml", "xmi:type", "elementType", "diagramType",
    "metaclass", "stereotype", "kind", "name"
}


def extract_content_hints(obj: Any) -> List[str]:
    """Extract a small set of textual hints from a JSON object (shallow).
    We only look at top-level and one-level-deep dicts/lists to stay cheap.
    """
    hints: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if (lk in {k.lower() for k in SIGNAL_KEYS}) and isinstance(v, (str, int, float)):
                hints.append(str(v))
            # Shallow dive into dict/list values
            if isinstance(v, dict):
                for kk, vv in v.items():
                    lkk = str(kk).lower()
                    if (lkk in {k.lower() for k in SIGNAL_KEYS}) and isinstance(vv, (str, int, float)):
                        hints.append(str(vv))
            elif isinstance(v, list):
                for item in v[:10]:  # limit to first few
                    if isinstance(item, dict):
                        for kk, vv in item.items():
                            lkk = str(kk).lower()
                            if (lkk in {k.lower() for k in SIGNAL_KEYS}) and isinstance(vv, (str, int, float)):
                                hints.append(str(vv))
    return hints


def classify_uml_for_diagram(
    json_files: List[str],
    classify_using: str = "filenames",  # 'filenames' | 'content' | 'both'
    max_files: Optional[int] = None,
) -> Dict[str, Any]:
    """Return UML classification dict for a diagram given its JSON files.

    Output:
      {
        "type": <UML type or "Unknown">,
        "category": "Structural"|"Behavioral"|"Unknown",
        "basis": "filenames"|"content"|"both"|"none",
        "score": {<type>: count, ...},
        "top_signals": ["keyword", ...]   # only filled if emit-signals is requested by caller
      }
    """
    classify_using = classify_using.lower()
    use_files = json_files if max_files is None else json_files[:max_files]

    type_scores = defaultdict(int)  # type -> score
    signals_collected: List[str] = []
    basis_seen = set()

    # 1) Filename-based signals
    if classify_using in ("filenames", "both"):
        for jf in use_files:
            base = os.path.splitext(os.path.basename(jf))[0].lower()
            for t, kws in UML_TYPES.items():
                for kw in kws:
                    if kw in base:
                        type_scores[t] += 1
                        signals_collected.append(kw)
                        basis_seen.add("filenames")

    # 2) Content-based signals (shallow + limited)
    if classify_using in ("content", "both"):
        for jf in use_files:
            ok, obj = safe_load_json(jf)
            if not ok or obj is None:
                continue
            hints = extract_content_hints(obj)
            # include base filename also as hint for content path
            base = os.path.splitext(os.path.basename(jf))[0]
            hints.append(base)
            blob = " ".join(str(h).lower() for h in hints)
            for t, kws in UML_TYPES.items():
                for kw in kws:
                    if kw in blob:
                        type_scores[t] += 1
                        signals_collected.append(kw)
                        basis_seen.add("content")

    if type_scores:
        # pick the top type by score; on tie, use precedence
        max_score = max(type_scores.values())
        candidates = [t for t, s in type_scores.items() if s == max_score]
        top_type = None
        for pref in TYPE_PRECEDENCE:
            if pref in candidates:
                top_type = pref
                break
        if top_type is None:
            top_type = candidates[0]
        cat = diagram_category(top_type)
        basis = "both" if basis_seen == {"filenames", "content"} else (next(iter(basis_seen)) if basis_seen else "none")
        return {
            "type": top_type,
            "category": cat,
            "basis": basis,
            "score": dict(sorted(type_scores.items(), key=lambda x: (-x[1], TYPE_PRECEDENCE.index(x[0]) if x[0] in TYPE_PRECEDENCE else 999))),
            "top_signals": []  # caller can fill if needed
        }
    else:
        return {"type": "Unknown", "category": "Unknown", "basis": "none", "score": {}, "top_signals": []}


# --- Collection from --root (optional) ----------------------------------------

def collect_diagram_ids_from_root(root: str, max_depth: int = 3) -> Dict[str, str]:
    """Return a mapping {uuid -> dir_path} discovered under --root.

    We walk up to `max_depth` levels deep and capture any directory whose name
    contains a UUID (tolerant). This is used solely for reconciliation/reporting.
    """
    mapping: Dict[str, str] = {}
    if not root or not os.path.isdir(root):
        return mapping

    root = os.path.abspath(root)
    root_depth = root.rstrip(os.sep).count(os.sep)

    for dp, dirnames, _ in os.walk(root):
        depth = dp.rstrip(os.sep).count(os.sep) - root_depth
        if depth > max_depth:
            # Prevent deep scans if not needed
            dirnames[:] = []
            continue
        for d in dirnames:
            uuids = extract_uuids(d) or extract_uuids(os.path.join(dp, d))
            for uid in uuids:
                # Last one wins if multiple map to same UUID
                mapping[uid] = os.path.join(dp, d)
    return mapping


# --- Collection from --extracted-json-root (authoritative grouping) -----------

def collect_extracted_jsons_by_diagram(
    exj_root: str,
    recursive: bool = False,
    validate_json: bool = False,
    max_diagrams: int | None = None,
    classify_using: str = "filenames",
    max_files_per_diagram: Optional[int] = None,
    emit_signals: bool = False,
) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """Return (by_diagram, orphan_dirs)

    by_diagram structure:
      {
        <uuid>: {
          "diagram_dir": <path>,
          "json_files": [paths...],
          "counts": {"total": N, "parsed_ok": X, "parse_failed": Y},
          "uml": {"type": str, "category": str, "basis": str, "score": {...}, "top_signals": [...]}
        },
        ...
      }

    Orphan dirs are directories under exj_root where no UUID could be extracted.
    """
    by_diagram: Dict[str, Dict[str, Any]] = {}
    orphan_dirs: List[str] = []

    if not os.path.isdir(exj_root):
        return by_diagram, orphan_dirs

    subdirs = list_immediate_subdirs(exj_root)
    if max_diagrams:
        subdirs = subdirs[:max_diagrams]

    for diagram_dir in subdirs:
        dir_name = os.path.basename(diagram_dir)
        uuids = extract_uuids(dir_name) or extract_uuids(diagram_dir)

        # Discover JSON files (one level by default, or recursive if requested)
        json_files = (
            list_json_files_recursive(diagram_dir) if recursive else
            list_json_files_nonrecursive(diagram_dir)
        )

        if not uuids:
            # No UUID in the directory name/path -> orphan bucket
            orphan_dirs.append(diagram_dir)
            continue

        # If multiple UUIDs are found, take the first one deterministically
        uid = uuids[0]

        parsed_ok = 0
        parse_failed = 0
        if validate_json:
            for jf in json_files:
                ok, _ = safe_validate_json(jf)
                if ok:
                    parsed_ok += 1
                else:
                    parse_failed += 1

        # UML type classification
        uml = classify_uml_for_diagram(
            json_files,
            classify_using=classify_using,
            max_files=max_files_per_diagram,
        )

        # include a short list of top signals if requested
        if emit_signals and uml.get("score"):
            # get most common 5 signals from the files scanned
            # We don't store per-file signals to keep memory small; instead we list top keywords by their contribution
            # based on the type score keys (keywords are not stored). As a proxy, show top scoring types.
            uml["top_signals"] = [t for t, _ in sorted(uml["score"].items(), key=lambda x: -x[1])[:5]]

        by_diagram[uid] = {
            "diagram_dir": diagram_dir,
            "json_files": sorted(json_files),
            "counts": {
                "total": len(json_files),
                "parsed_ok": parsed_ok,
                "parse_failed": parse_failed,
            },
            "uml": uml,
        }

    return by_diagram, orphan_dirs


# --- Reconciliation + Output building ----------------------------------------

def build_output(
    ids_from_root: Dict[str, str],
    by_diagram: Dict[str, Dict[str, Any]],
    orphan_dirs: List[str],
) -> Dict[str, Any]:
    root_ids = set(ids_from_root.keys())
    exj_ids = set(by_diagram.keys())

    missing_groups = sorted(root_ids - exj_ids)  # present in --root but missing in extracted
    orphans_by_id = sorted(exj_ids - root_ids)   # present in extracted but not in --root

    output = {
        "GroupedClassJSON": {
            "by_diagram": [
                {
                    "diagram_id": did,
                    "diagram_dir": by_diagram[did]["diagram_dir"],
                    "json_files": by_diagram[did]["json_files"],
                    "counts": by_diagram[did]["counts"],
                    "uml": by_diagram[did]["uml"],
                }
                for did in sorted(by_diagram.keys())
            ],
            "missing_groups": missing_groups,
            # Report both directory-orphans (no UUID in name) and ID-orphans (no match in --root)
            "orphan_group_dirs": sorted(orphan_dirs),
            "orphan_group_ids": orphans_by_id,
            "stats": {
                "extracted_diagram_dirs": len(by_diagram),
                "dir_without_uuid": len(orphan_dirs),
                "root_ids": len(root_ids),
                "intersection": len(root_ids & exj_ids),
            },
        }
    }
    return output


# --- CLI ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Group extracted UML class JSONs by diagram UUID and classify UML type.")
    p.add_argument("--extracted-json-root", required=True,
                   help="Path to the parent directory containing <diagram_uuid>/ subdirectories with *.json files.")
    p.add_argument("--out-json", required=True, help="Path to write the summary JSON output.")
    p.add_argument("--root", default=None,
                   help="(Optional) Root of UML diagram source tree for reconciliation. Not required for grouping.")
    p.add_argument("--recursive", action="store_true",
                   help="Recursively search for JSON files under each diagram directory (default: non-recursive).")
    p.add_argument("--validate-json", action="store_true",
                   help="Attempt to parse each JSON file to count parsed_ok/failed (slower). Contents are not stored.")
    p.add_argument("--max-diagrams", type=int, default=None,
                   help="Limit the number of diagram directories to process (for quick sanity checks).")

    # NEW classification options
    p.add_argument("--classify-using", choices=["filenames", "content", "both"], default="filenames",
                   help="Basis for UML type classification: filenames (fast), content (slower), both (best).")
    p.add_argument("--max-files-per-diagram", type=int, default=None,
                   help="When classifying via content/both, cap the number of files inspected per diagram.")
    p.add_argument("--emit-signals", action="store_true",
                   help="Include a short 'top_signals' list in the output for debugging.")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    exj_root = os.path.abspath(args.extracted_json_root)
    out_json = os.path.abspath(args.out_json)
    root = os.path.abspath(args.root) if args.root else None

    if not os.path.isdir(exj_root):
        raise SystemExit(f"--extracted-json-root is not a directory: {exj_root}")

    # 1) Authoritative grouping from extracted-json-root + classification
    by_diagram, orphan_dirs = collect_extracted_jsons_by_diagram(
        exj_root,
        recursive=args.recursive,
        validate_json=args.validate_json,
        max_diagrams=args.max_diagrams,
        classify_using=args.classify_using,
        max_files_per_diagram=args.max_files_per_diagram,
        emit_signals=args.emit_signals,
    )

    # 2) Optional reconciliation with --root (if provided)
    ids_from_root: Dict[str, str] = {}
    if root:
        ids_from_root = collect_diagram_ids_from_root(root)

    # 3) Build output and write
    output = build_output(ids_from_root, by_diagram, orphan_dirs)

    os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # 4) Console summary
    root_ids = set(ids_from_root.keys())
    exj_ids = set(by_diagram.keys())

    print("\n[Summary]")
    print(f"  Extracted JSON root : {exj_root}")
    if root:
        print(f"  UML root (optional) : {root}")
    print(f"  Output JSON          : {out_json}")

    print(f"\n  Diagram dirs discovered under extracted root : {len(by_diagram) + len(orphan_dirs)}")
    print(f"  - with UUID (grouped)                       : {len(by_diagram)}")
    print(f"  - without UUID (orphan dirs)                : {len(orphan_dirs)}")

    # Classification summary
    type_counts = defaultdict(int)
    for info in by_diagram.values():
        t = info.get("uml", {}).get("type", "Unknown")
        type_counts[t] += 1
    print("\n  UML type counts (top 10):")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {t:20s} : {c}")

    if args.validate_json:
        total_files = sum(v["counts"]["total"] for v in by_diagram.values())
        parsed_ok = sum(v["counts"]["parsed_ok"] for v in by_diagram.values())
        parse_failed = sum(v["counts"]["parse_failed"] for v in by_diagram.values())
        print(f"\n  JSON files discovered                         : {total_files}\n  - parsed OK                                    : {parsed_ok}\n  - parse failed                                 : {parse_failed}")

    if root:
        print(f"\n  --root IDs found                              : {len(root_ids)}")
        print(f"  Intersection (--root ∩ extracted)            : {len(root_ids & exj_ids)}")
        print(f"  Only in --root (missing_groups)              : {len(root_ids - exj_ids)}")
        print(f"  Only in extracted (orphan_group_ids)         : {len(exj_ids - root_ids)}")

    print("\nDone.")


if __name__ == "__main__":
    main()
