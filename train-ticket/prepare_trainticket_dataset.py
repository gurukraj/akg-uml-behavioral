#!/usr/bin/env python3
"""
Pre-processing script for Train-Ticket UML datasets.

Converts the per-file UML diagram data into the consolidated behavioral JSON
format expected by the AKG pipeline (GenMyModel-compatible schema).

Handles:
  - Sequence diagrams: already in correct interaction_*.json format (copy as-is)
  - Activity diagrams: consolidates individual node/edge/partition files into
    activity_*.json with full node objects, edge objects, and partition objects
  - Communication diagrams: converts collaboration_*.json + object/message files
    into interaction_*.json format with synthetic occurrence fragments
  - Class diagrams: copies as structural context
  - Creates the behavioral JSON index expected by run_akg_pipeline.py

Usage:
  python prepare_trainticket_dataset.py \
      --source /path/to/train-ticket/uml-diagrams \
      --output /path/to/processed/train-ticket \
      --project-name "Train-Ticket"
"""

import argparse
import json
import os
import shutil
import uuid
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def gen_key() -> str:
    return "_" + uuid.uuid4().hex[:24]


def load_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  WARNING: cannot read {path}: {e}")
        return None


def write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def synthesize_execution_specifications(interaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize BehaviorExecutionSpecification fragments from the message flow.
    
    The AKG pipeline uses execution specifications to reconstruct call-chain
    depth (causality). Without them, all messages have depth=1 and Q1
    (Synchronous Call Chain > 3) cannot fire.
    
    Algorithm:
    1. For each synchCall message received by lifeline L:
       - Create a BehaviorExecutionSpecification on L
       - start = receiveEvent of the synchCall
       - finish = sendEvent of the matching reply from L, or the last
         send from L before the next receive on L from the same sender
    2. For the root execution (first synchCall to a service):
       - The execution spans from receive to the final reply
    """
    messages = interaction.get("messages", [])
    fragments = interaction.get("fragments", [])
    lifelines = interaction.get("lifelines", [])
    
    if not messages or not fragments:
        return interaction
    
    # Build fragment lookup
    frag_by_key = {f["key"]: f for f in fragments}
    
    # Build message lookup by key
    msg_by_key = {m["key"]: m for m in messages}
    
    # For each message, resolve sender/receiver lifeline
    msg_info = []
    for i, m in enumerate(messages):
        send_fr = frag_by_key.get(m.get("sendEvent", ""))
        recv_fr = frag_by_key.get(m.get("receiveEvent", ""))
        sender_ll = send_fr["covered"] if send_fr and send_fr.get("covered") else None
        receiver_ll = recv_fr["covered"] if recv_fr and recv_fr.get("covered") else None
        
        # Determine position from fragment order
        send_idx = None
        recv_idx = None
        for fi, f in enumerate(fragments):
            if f["key"] == m.get("sendEvent"):
                send_idx = fi
            if f["key"] == m.get("receiveEvent"):
                recv_idx = fi
        
        msg_info.append({
            "msg": m,
            "index": i,
            "send_idx": send_idx,
            "recv_idx": recv_idx,
            "sender_ll": sender_ll,
            "receiver_ll": receiver_ll,
            "sort": m.get("messageSort", ""),
        })
    
    # Create execution specifications
    exec_specs = []
    
    # For each synchCall, find the matching reply and create an execution spec
    # on the receiver lifeline
    for i, mi in enumerate(msg_info):
        if mi["sort"] != "synchCall":
            continue
        if not mi["receiver_ll"] or not mi["sender_ll"]:
            continue
        
        receiver = mi["receiver_ll"]
        sender = mi["sender_ll"]
        recv_event_key = mi["msg"].get("receiveEvent")
        
        if not recv_event_key:
            continue
        
        # Find the matching reply: a reply from receiver back to sender
        # that comes after this message
        finish_event_key = None
        nesting_depth = 0
        
        for j in range(i + 1, len(msg_info)):
            mj = msg_info[j]
            
            # Track nesting: if receiver sends another synchCall, depth increases
            if (mj["sort"] == "synchCall" and mj["sender_ll"] == receiver):
                nesting_depth += 1
            
            # If receiver sends a reply back to sender at the right nesting level
            if (mj["sort"] == "reply" and 
                mj["sender_ll"] == receiver and 
                mj["receiver_ll"] == sender and
                nesting_depth == 0):
                finish_event_key = mj["msg"].get("sendEvent")
                break
            
            # Track nesting reduction
            if (mj["sort"] == "reply" and mj["sender_ll"] == receiver):
                if nesting_depth > 0:
                    nesting_depth -= 1
        
        # If no reply found, use the last fragment involving this receiver
        if not finish_event_key:
            for f in reversed(fragments):
                if f.get("covered") == receiver:
                    finish_event_key = f["key"]
                    break
        
        if finish_event_key and finish_event_key != recv_event_key:
            exec_key = gen_key()
            exec_specs.append({
                "key": exec_key,
                "type": "uml:BehaviorExecutionSpecification",
                "name": None,
                "covered": receiver,
                "enclosingInteraction": interaction.get("name", ""),
                "message": None,
                "execution": None,
                "start": recv_event_key,
                "finish": finish_event_key
            })
    
    # Add execution specs to fragments
    if exec_specs:
        interaction = copy.deepcopy(interaction)
        interaction["fragments"] = fragments + exec_specs
    
    return interaction


def classify_element_file(filename: str) -> str:
    """Classify a per-element JSON file by its name/content pattern."""
    lower = filename.lower()
    if filename == '_diagram_info.json':
        return 'diagram_info'
    if filename == '_master_index.json':
        return 'skip'
    if filename.endswith('.py'):
        return 'skip'
    if filename.startswith('interaction_'):
        return 'interaction'
    if filename.startswith('activity_'):
        return 'activity'
    if filename.startswith('statemachine_'):
        return 'statemachine'
    if filename.startswith('collaboration_'):
        return 'collaboration'
    if filename.startswith('controlflow_'):
        return 'controlflow'
    if filename.startswith('partition_'):
        return 'partition'
    if filename.startswith('message_'):
        return 'message'
    if filename.startswith('association_'):
        return 'association'
    if filename.startswith('dependency_'):
        return 'dependency'
    if filename.startswith('component_'):
        return 'component'
    # Node-type files for activity diagrams
    for prefix in ('InitialNode', 'FinalNode', 'DecisionNode', 'ForkNode',
                   'JoinNode', 'MergeNode', 'FlowFinalNode'):
        if filename.startswith(prefix):
            return 'activity_node'
    return 'class_or_object'


def consolidate_activity(diagram_dir: str, diagram_id: str) -> Tuple[Optional[Dict], Dict]:
    """
    Read all individual activity files and consolidate into the format
    expected by parse_activity() in behavioral_source_model.py.

    Expected output format:
    {
        "name": "...", "key": "...", "type": "uml:Activity",
        "nodes": [ {key, name, nodeType, inPartition, incoming, outgoing}, ... ],
        "edges": [ {key, name, edgeType, source, target, guard}, ... ],
        "partitions": [ {key, name, nodes: [...]}, ... ],
        "nodeCount": N, "edgeCount": N, "partitionCount": N,
        "nodeTypeCounts": {...}, "file_path": "..."
    }
    """
    activity_data = None
    nodes = []
    edges = []
    partitions = []
    node_keys = set()

    files = sorted(os.listdir(diagram_dir))
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(diagram_dir, fname)
        ftype = classify_element_file(fname)

        if ftype == 'activity':
            data = load_json(fpath)
            if data:
                activity_data = data

        elif ftype == 'controlflow':
            data = load_json(fpath)
            if data:
                edges.append({
                    "name": data.get("name"),
                    "key": data.get("key", gen_key()),
                    "edgeType": data.get("type", "uml:ControlFlow"),
                    "source": data.get("source"),
                    "target": data.get("target"),
                    "guard": data.get("guard")
                })

        elif ftype == 'partition':
            data = load_json(fpath)
            if data:
                partitions.append({
                    "name": data.get("name"),
                    "key": data.get("key", gen_key()),
                    "nodes": data.get("nodes", [])
                })

        elif ftype == 'activity_node':
            data = load_json(fpath)
            if data:
                node_type = data.get("type", "uml:OpaqueAction")
                node_key = data.get("key", gen_key())
                nodes.append({
                    "name": data.get("name"),
                    "key": node_key,
                    "nodeType": node_type,
                    "inPartition": None,
                    "incoming": [],
                    "outgoing": []
                })
                node_keys.add(node_key)

        elif ftype == 'class_or_object':
            # Could be an action node (OpaqueAction) file
            data = load_json(fpath)
            if data and data.get("type") in ("uml:OpaqueAction", "uml:Action",
                                              "uml:CallBehaviorAction",
                                              "uml:SendSignalAction"):
                node_key = data.get("key", gen_key())
                nodes.append({
                    "name": data.get("name"),
                    "key": node_key,
                    "nodeType": data.get("type", "uml:OpaqueAction"),
                    "inPartition": None,
                    "incoming": [],
                    "outgoing": []
                })
                node_keys.add(node_key)
            elif data and data.get("key") and data.get("type") is None:
                # Files like SearchTrips.json, SelectTrip.json etc.
                # These are action nodes without an explicit type
                node_key = data.get("key", gen_key())
                if node_key not in node_keys:
                    nodes.append({
                        "name": data.get("name"),
                        "key": node_key,
                        "nodeType": "uml:OpaqueAction",
                        "inPartition": None,
                        "incoming": [],
                        "outgoing": []
                    })
                    node_keys.add(node_key)

    if not activity_data:
        return None, {}

    # Check if activity_data has node keys we haven't picked up yet
    # (the activity file references nodes by key)
    activity_node_keys = set()
    if isinstance(activity_data.get("nodes"), list):
        for item in activity_data["nodes"]:
            if isinstance(item, str):
                activity_node_keys.add(item)

    # Build partition index: node_key -> partition_key
    partition_index = {}
    for p in partitions:
        for nk in p.get("nodes", []):
            partition_index[nk] = p["key"]

    # Set inPartition for nodes
    for node in nodes:
        pk = partition_index.get(node["key"])
        if pk:
            node["inPartition"] = pk

    # Compute incoming/outgoing from edges
    node_incoming = {}
    node_outgoing = {}
    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if src:
            node_outgoing.setdefault(src, []).append(edge["key"])
        if tgt:
            node_incoming.setdefault(tgt, []).append(edge["key"])

    for node in nodes:
        node["incoming"] = node_incoming.get(node["key"], [])
        node["outgoing"] = node_outgoing.get(node["key"], [])

    # Count node types
    node_type_counts = {}
    for node in nodes:
        nt = node.get("nodeType", "unknown")
        node_type_counts[nt] = node_type_counts.get(nt, 0) + 1

    consolidated = {
        "name": activity_data.get("name", diagram_id),
        "key": activity_data.get("key", gen_key()),
        "type": activity_data.get("type", "uml:Activity"),
        "nodes": nodes,
        "edges": edges,
        "partitions": partitions,
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "partitionCount": len(partitions),
        "nodeTypeCounts": node_type_counts,
        "file_path": diagram_id
    }

    stats = {
        "nodes": len(nodes),
        "edges": len(edges),
        "partitions": len(partitions),
        "node_types": node_type_counts
    }

    return consolidated, stats


def convert_communication_to_interaction(
    diagram_dir: str, diagram_id: str
) -> Tuple[Optional[Dict], Dict]:
    """
    Convert communication diagram files (collaboration, objects, messages)
    into the interaction_*.json format expected by the AKG pipeline.

    Communication messages have explicit sender/receiver keys.
    We create synthetic occurrence fragments to bridge to the interaction format.
    """
    collaboration_data = None
    objects = {}  # key -> {name, key, type}
    messages = []  # list of message dicts

    files = sorted(os.listdir(diagram_dir))
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(diagram_dir, fname)
        ftype = classify_element_file(fname)

        if ftype == 'collaboration':
            data = load_json(fpath)
            if data:
                collaboration_data = data

        elif ftype == 'message':
            data = load_json(fpath)
            if data:
                messages.append(data)

        elif ftype in ('class_or_object',):
            data = load_json(fpath)
            if data and data.get("key"):
                # These are collaboration objects (lifelines)
                obj_type = data.get("type", "")
                if obj_type not in ("class", "interface", "dependency",
                                    "association", "uml:Component"):
                    objects[data["key"]] = data

    if not collaboration_data:
        return None, {}

    # Also check for objects referenced in collaboration but not yet found
    for obj_key in (collaboration_data.get("objects") or []):
        if isinstance(obj_key, str) and obj_key not in objects:
            # Try to find the object file
            for fname in files:
                if not fname.endswith('.json'):
                    continue
                fpath = os.path.join(diagram_dir, fname)
                data = load_json(fpath)
                if data and data.get("key") == obj_key:
                    objects[obj_key] = data
                    break

    # Build lifelines from objects
    lifelines = []
    for obj_key, obj_data in objects.items():
        lifelines.append({
            "name": obj_data.get("name", f"object_{obj_key[:8]}"),
            "key": obj_key,
            "represents": gen_key(),
            "coveredBy": []
        })

    # Sort messages by their label number if available
    def msg_sort_key(m):
        label = m.get("messageLabel", m.get("name", ""))
        # Extract leading number from label like "3.1: queryForTravel()"
        parts = label.split(":")
        if parts:
            num_part = parts[0].strip()
            try:
                # Handle dotted numbers like "3.1.1"
                segments = num_part.split(".")
                return tuple(int(s) for s in segments if s.isdigit())
            except (ValueError, IndexError):
                pass
        return (999,)

    messages.sort(key=msg_sort_key)

    # Create message objects and synthetic fragments
    interaction_messages = []
    fragments = []
    frag_index = 0

    for msg in messages:
        msg_key = msg.get("key", gen_key())
        sender_key = msg.get("sender")
        receiver_key = msg.get("receiver")
        msg_name = msg.get("name") or msg.get("messageLabel", "")

        # Create send event fragment
        send_event_key = gen_key()
        fragments.append({
            "key": send_event_key,
            "type": "uml:MessageOccurrenceSpecification",
            "name": None,
            "covered": sender_key,
            "enclosingInteraction": diagram_id,
            "message": msg_key,
            "execution": None
        })
        frag_index += 1

        # Create receive event fragment
        recv_event_key = gen_key()
        fragments.append({
            "key": recv_event_key,
            "type": "uml:MessageOccurrenceSpecification",
            "name": None,
            "covered": receiver_key,
            "enclosingInteraction": diagram_id,
            "message": msg_key,
            "execution": None
        })
        frag_index += 1

        interaction_messages.append({
            "name": msg_name,
            "key": msg_key,
            "messageSort": "synchCall",
            "sendEvent": send_event_key,
            "receiveEvent": recv_event_key,
            "connector": None,
            "signature": None
        })

    interaction = {
        "name": collaboration_data.get("name", diagram_id),
        "key": collaboration_data.get("key", gen_key()),
        "type": "interaction",
        "lifelines": lifelines,
        "messages": interaction_messages,
        "fragments": fragments
    }

    stats = {
        "lifelines": len(lifelines),
        "messages": len(interaction_messages),
        "fragments": len(fragments)
    }

    return interaction, stats


def process_dataset(source_dir: str, output_dir: str, project_name: str) -> Dict:
    """Process an entire UML dataset and prepare it for the AKG pipeline."""

    print(f"\n{'='*70}")
    print(f"Processing: {project_name}")
    print(f"Source: {source_dir}")
    print(f"Output: {output_dir}")
    print(f"{'='*70}")

    os.makedirs(output_dir, exist_ok=True)

    # Read master index
    master_index_path = os.path.join(source_dir, '_master_index.json')
    if not os.path.exists(master_index_path):
        print(f"ERROR: _master_index.json not found in {source_dir}")
        return {}

    master_index = load_json(master_index_path)
    if not master_index:
        print("ERROR: could not parse _master_index.json")
        return {}

    diagrams = master_index.get("diagrams", [])
    print(f"Found {len(diagrams)} diagrams in master index")

    behavioral_entries = []
    structural_entries = []
    summary = {
        "project": project_name,
        "source": source_dir,
        "total_diagrams": len(diagrams),
        "behavioral_diagrams": 0,
        "sequence_diagrams": 0,
        "activity_diagrams": 0,
        "communication_diagrams": 0,
        "class_diagrams": 0,
        "processing_log": []
    }

    for diag in diagrams:
        diagram_id = diag.get("diagram_id", "")
        primary_type = diag.get("primary_type", "")
        is_behavioral = diag.get("is_behavioral", False)

        src_dir = os.path.join(source_dir, diagram_id)
        out_dir = os.path.join(output_dir, diagram_id)

        if not os.path.isdir(src_dir):
            msg = f"  SKIP {diagram_id}: source directory not found"
            print(msg)
            summary["processing_log"].append(msg)
            continue

        print(f"\n  Processing: {diagram_id} (type={primary_type}, behavioral={is_behavioral})")

        if primary_type == "Sequence":
            # Sequence diagrams: copy interaction_*.json and _diagram_info.json
            os.makedirs(out_dir, exist_ok=True)
            files = os.listdir(src_dir)
            copied_interaction = False

            for fname in files:
                if not fname.endswith('.json'):
                    continue
                src_path = os.path.join(src_dir, fname)
                dst_path = os.path.join(out_dir, fname)
                ftype = classify_element_file(fname)

                if ftype == 'interaction':
                    # Read, synthesize execution specs, then write
                    interaction_data = load_json(src_path)
                    if interaction_data:
                        enriched = synthesize_execution_specifications(interaction_data)
                        n_exec = len(enriched.get("fragments", [])) - len(interaction_data.get("fragments", []))
                        write_json(dst_path, enriched)
                        copied_interaction = True
                        msg = f"    Enriched interaction: {fname} (+{n_exec} execution specs)"
                        print(msg)
                elif ftype == 'diagram_info':
                    shutil.copy2(src_path, dst_path)
                elif ftype in ('class_or_object', 'association', 'dependency'):
                    # Copy structural context files
                    shutil.copy2(src_path, dst_path)

            if copied_interaction:
                behavioral_entries.append({
                    "diagram_dir": os.path.abspath(out_dir),
                    "uml": {"type": "Sequence"}
                })
                summary["sequence_diagrams"] += 1
                summary["behavioral_diagrams"] += 1
                summary["processing_log"].append(
                    f"  OK {diagram_id}: Sequence diagram copied")
            else:
                msg = f"    WARNING: no interaction_*.json found in {diagram_id}"
                print(msg)
                summary["processing_log"].append(msg)

        elif primary_type == "Activity":
            # Activity diagrams: consolidate individual files
            os.makedirs(out_dir, exist_ok=True)
            activity_json, stats = consolidate_activity(src_dir, diagram_id)

            if activity_json:
                # Write consolidated activity file
                activity_name = activity_json.get("name", diagram_id)
                activity_fname = f"activity_{activity_name.replace(' ', '_')}.json"
                write_json(os.path.join(out_dir, activity_fname), activity_json)

                # Copy or create _diagram_info.json
                src_info = os.path.join(src_dir, '_diagram_info.json')
                if os.path.exists(src_info):
                    shutil.copy2(src_info, os.path.join(out_dir, '_diagram_info.json'))
                else:
                    write_json(os.path.join(out_dir, '_diagram_info.json'), {
                        "classification": {
                            "categories": ["Activity"],
                            "primary": "Activity",
                            "is_class_diagram": False,
                            "is_behavioral": True
                        },
                        "detectedTypes": stats.get("node_types", {}),
                        "diagram_id": diagram_id
                    })

                behavioral_entries.append({
                    "diagram_dir": os.path.abspath(out_dir),
                    "uml": {"type": "Activity"}
                })
                summary["activity_diagrams"] += 1
                summary["behavioral_diagrams"] += 1
                msg = (f"  OK {diagram_id}: Activity consolidated "
                       f"({stats['nodes']} nodes, {stats['edges']} edges, "
                       f"{stats['partitions']} partitions)")
                print(f"    {msg}")
                summary["processing_log"].append(msg)
            else:
                msg = f"    WARNING: no activity data found in {diagram_id}"
                print(msg)
                summary["processing_log"].append(msg)

        elif primary_type == "Communication":
            # Communication diagrams: convert to interaction format
            os.makedirs(out_dir, exist_ok=True)
            interaction_json, stats = convert_communication_to_interaction(
                src_dir, diagram_id)

            if interaction_json:
                # Write as interaction file
                interaction_name = interaction_json.get("name", diagram_id)
                interaction_fname = f"interaction_{interaction_name.replace(' ', '_')}.json"
                write_json(os.path.join(out_dir, interaction_fname), interaction_json)

                # Create diagram info that declares it as Communication
                write_json(os.path.join(out_dir, '_diagram_info.json'), {
                    "classification": {
                        "categories": ["Communication"],
                        "primary": "Communication",
                        "is_class_diagram": False,
                        "is_behavioral": True
                    },
                    "detectedTypes": {
                        "uml:Collaboration": 1,
                        "uml:LifelineOrObject": stats.get("lifelines", 0),
                        "uml:Message": stats.get("messages", 0)
                    },
                    "diagram_id": diagram_id
                })

                behavioral_entries.append({
                    "diagram_dir": os.path.abspath(out_dir),
                    "uml": {"type": "Communication"}
                })
                summary["communication_diagrams"] += 1
                summary["behavioral_diagrams"] += 1
                msg = (f"  OK {diagram_id}: Communication→Interaction "
                       f"({stats['lifelines']} lifelines, {stats['messages']} messages)")
                print(f"    {msg}")
                summary["processing_log"].append(msg)
            else:
                msg = f"    WARNING: no collaboration data found in {diagram_id}"
                print(msg)
                summary["processing_log"].append(msg)

        elif primary_type == "Class":
            # Class diagrams: copy for structural context
            os.makedirs(out_dir, exist_ok=True)
            files = os.listdir(src_dir)
            for fname in files:
                if not fname.endswith('.json'):
                    continue
                shutil.copy2(
                    os.path.join(src_dir, fname),
                    os.path.join(out_dir, fname)
                )
            structural_entries.append({
                "diagram_dir": os.path.abspath(out_dir),
                "uml": {"type": "Class"}
            })
            summary["class_diagrams"] += 1

        elif primary_type == "Component":
            # Component diagrams: copy for reference
            os.makedirs(out_dir, exist_ok=True)
            files = os.listdir(src_dir)
            for fname in files:
                if not fname.endswith('.json'):
                    continue
                shutil.copy2(
                    os.path.join(src_dir, fname),
                    os.path.join(out_dir, fname)
                )
            summary["processing_log"].append(
                f"  INFO {diagram_id}: Component diagram copied for reference")

        else:
            msg = f"  SKIP {diagram_id}: unrecognized type {primary_type}"
            print(msg)
            summary["processing_log"].append(msg)

    # Create the behavioral JSON index expected by the AKG pipeline
    behavioral_index = {
        "metadata": {
            "description": f"AKG behavioral index for {project_name}",
            "source_dataset": project_name,
            "source_directory": source_dir,
            "target_diagram_types": ["Sequence", "Activity", "Communication",
                                     "StateMachine"]
        },
        "primary_behavioral_diagrams": behavioral_entries,
        "score_signal_behavioral_diagrams": structural_entries
    }

    index_path = os.path.join(output_dir, "behavioral_index.json")
    write_json(index_path, behavioral_index)
    print(f"\n  Behavioral index written: {index_path}")
    print(f"  Total behavioral diagrams: {summary['behavioral_diagrams']}")
    print(f"    Sequence: {summary['sequence_diagrams']}")
    print(f"    Activity: {summary['activity_diagrams']}")
    print(f"    Communication: {summary['communication_diagrams']}")
    print(f"  Structural diagrams (context): {summary['class_diagrams']}")

    # Write processing summary
    summary_path = os.path.join(output_dir, "processing_summary.json")
    write_json(summary_path, summary)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Prepare Train-Ticket UML dataset for the AKG pipeline")
    parser.add_argument("--source", required=True,
                        help="Source UML diagrams directory")
    parser.add_argument("--output", required=True,
                        help="Output directory for processed data")
    parser.add_argument("--project-name", default="Train-Ticket",
                        help="Project name for index metadata")
    args = parser.parse_args()

    process_dataset(args.source, args.output, args.project_name)


if __name__ == "__main__":
    main()
