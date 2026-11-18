#!/usr/bin/env python3
"""
4_extract_all_uml_information.py

Enhanced version of 3_extract_uml_information.py that extracts ALL types of
UML diagram elements from XMI files — not just Class diagrams.

Supported UML element types:
  Structural: Class, Interface, Enumeration, DataType, Package, Component,
              Node, Device, ExecutionEnvironment, Association, AssociationClass,
              Dependency, Usage, InstanceSpecification, InformationFlow,
              CommunicationPath
  Behavioral: Interaction (Sequence/Communication), Activity, StateMachine,
              UseCase, Actor, Collaboration

Output structure per diagram:
  output_folder/<diagram_id>/
    _diagram_info.json              -- Metadata: detected types, classification, counts
    <ClassName>.json                -- Class elements (backward-compatible format)
    <InterfaceName>.json            -- Interface elements
    enum_<EnumName>.json            -- Enumeration elements
    datatype_<DataTypeName>.json    -- DataType elements
    interaction_<Name>.json         -- Interaction (Sequence) elements
    activity_<Name>.json            -- Activity elements
    statemachine_<Name>.json        -- StateMachine elements
    usecase_<Name>.json             -- UseCase elements
    actor_<Name>.json               -- Actor elements
    component_<Name>.json           -- Component elements
    association_<ID>.json           -- Association elements
    dependency_<ID>.json            -- Dependency elements
    instance_<Name>.json            -- InstanceSpecification elements
    package_<Name>.json             -- Package elements (top-level only)
    node_<Name>.json                -- Deployment Node/Device elements
    collaboration_<Name>.json       -- Collaboration elements

Usage:
  # Mode 1: Extract all UML elements from XMI files
  python 4_extract_all_uml_information.py extract-xmi <path_to_xmi_folder> [--output_folder <path>]

  # Mode 2: Extract behavioral diagrams from classification JSON
  python 4_extract_all_uml_information.py extract-behavioral <classification_json> [--output_json <path>]

Examples:
  python 4_extract_all_uml_information.py extract-xmi ../1_UML-Diagrams/1_UML-Diagrams
  python 4_extract_all_uml_information.py extract-xmi ../1_UML-Diagrams/1_UML-Diagrams --output_folder ../4_Extracted-All-UML-Informations
  python 4_extract_all_uml_information.py extract-behavioral ../../UML_All_Diagram_Classification_Extraction_Latest.json --output_json ../../akg-implementation/UML_Behavioral_Diagrams_Extracted.json
"""

import os
import argparse
import xml.etree.ElementTree as ET
import shutil
import json
import time
import sys
from collections import defaultdict


# ─── Namespaces ───────────────────────────────────────────────────────────────

NS = {
    'xmi': 'http://schema.omg.org/spec/XMI/2.1',
    'uml': 'http://www.eclipse.org/uml2/5.0.0/UML',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

XSI_TYPE = '{http://www.w3.org/2001/XMLSchema-instance}type'
XMI_TYPE = '{http://schema.omg.org/spec/XMI/2.1}type'
XMI_ID   = '{http://schema.omg.org/spec/XMI/2.1}id'


# ─── UML Type Constants ──────────────────────────────────────────────────────

# Types to skip when counting (utility types, not standalone diagram elements)
SKIP_TYPES = {
    'uml:PrimitiveType', 'uml:LiteralInteger', 'uml:LiteralUnlimitedNatural',
    'uml:LiteralString', 'uml:Expression', 'uml:InstanceValue',
    'uml:ClassifierTemplateParameter', 'uml:RedefinableTemplateSignature',
}


# ─── Utility Functions ────────────────────────────────────────────────────────

def format_time(seconds):
    # Convert seconds to hours, minutes, and seconds, then format as XXh YYm ZZs
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s"


def get_elem_id(elem):
    """Get XMI ID of an element."""
    return elem.get(XMI_ID)


def get_elem_type(elem):
    """Get xsi:type or xmi:type of an element."""
    return elem.get(XSI_TYPE) or elem.get(XMI_TYPE)


def get_name(elem):
    """Get the 'name' attribute of an element, stripped and space-removed."""
    try:
        name = elem.attrib['name']
        name = name.strip().replace(" ", "")
        return name if name else None
    except (KeyError, AttributeError):
        return None


def get_modifiers(elem):
    """Get visibility modifier of an element."""
    visibility = elem.attrib.get('visibility')
    return [visibility] if visibility else []


def safe_file_name(name):
    """Sanitize a name for use as a file path component."""
    if not name:
        return "_unnamed"
    return (name.replace("/", "_").replace("\\", "_").replace(":", "_")
            .replace("*", "_").replace("?", "_").replace('"', "_")
            .replace("<", "_").replace(">", "_").replace("|", "_"))


def find_elements_by_type(root, uml_type):
    """Find all packagedElement with given xsi:type or xmi:type, de-duplicated."""
    results = []
    results += root.findall(f".//packagedElement[@xsi:type='{uml_type}']", NS)
    results += root.findall(f".//packagedElement[@xmi:type='{uml_type}']", NS)
    # De-duplicate preserving order
    seen = set()
    unique = []
    for e in results:
        eid = id(e)
        if eid not in seen:
            seen.add(eid)
            unique.append(e)
    return unique


# ─── Diagram Type Detection ──────────────────────────────────────────────────

def detect_diagram_types(root):
    """Detect which UML element types are present in the XMI document."""
    type_counts = defaultdict(int)
    for elem in root.iter():
        uml_type = get_elem_type(elem)
        if uml_type and uml_type not in SKIP_TYPES:
            type_counts[uml_type] += 1
    return dict(type_counts)


def classify_diagram(type_counts):
    """Classify the overall diagram type based on detected elements."""
    categories = []
    has = lambda t: t in type_counts

    # Check for behavioral diagram types
    if has('uml:Interaction'):
        categories.append('Sequence')
    if has('uml:Activity'):
        categories.append('Activity')
    if has('uml:StateMachine'):
        categories.append('StateMachine')
    if has('uml:UseCase') or has('uml:Actor'):
        categories.append('UseCase')
    if has('uml:Collaboration') and not has('uml:Interaction'):
        categories.append('Communication')

    # Check for structural types
    if has('uml:Class') or has('uml:Interface') or has('uml:Enumeration'):
        categories.append('Class')
    if has('uml:Component'):
        categories.append('Component')
    if has('uml:Node') or has('uml:Device') or has('uml:ExecutionEnvironment'):
        categories.append('Deployment')
    if has('uml:InstanceSpecification') and not any(
            c in categories for c in ['Class', 'Sequence', 'Activity']):
        categories.append('Object')
    if has('uml:Package') and not categories:
        categories.append('Package')

    if not categories:
        categories.append('Unknown')

    is_class_diagram = 'Class' in categories
    return {
        'categories': categories,
        'primary': categories[0],
        'is_class_diagram': is_class_diagram,
        'is_behavioral': any(c in categories for c in
                            ['Sequence', 'Activity', 'StateMachine',
                             'Communication', 'UseCase']),
    }


# ─── Extraction: Shared Lookups ──────────────────────────────────────────────

def extract_generalizations(root):
    """Extract all generalizations from the XMI root."""
    generalizations = {}
    for gen_elem in root.findall(".//generalization"):
        specific = gen_elem.attrib.get('specific')
        general = gen_elem.attrib.get('general')
        if specific and general:
            generalizations.setdefault(specific, []).append(general)
    return generalizations


def extract_interface_realizations(root):
    """Extract all interface realizations."""
    realizations = {}
    for real_elem in root.findall(".//interfaceRealization"):
        client = real_elem.attrib.get('client')
        contract = real_elem.attrib.get('contract')
        if client and contract:
            realizations.setdefault(client, []).append(contract)
    return realizations


# ─── Extraction: Fields (ownedAttribute) ─────────────────────────────────────

def extract_fields(elem, owner_key):
    """Extract ownedAttribute elements (fields) from a classifier."""
    fields = {}
    for field_elem in elem.findall(".//ownedAttribute", NS):
        # Skip association-owned ends
        if field_elem.attrib.get('association'):
            continue
        field_name = get_name(field_elem)
        if field_name is None:
            continue

        field_key = get_elem_id(field_elem)
        field_type_ref = field_elem.attrib.get('type')
        type_elem = field_elem.find("type", NS)
        field_type_href = (type_elem.attrib.get('href')
                           if type_elem is not None else None)

        fields[field_name] = {
            "name": field_name,
            "key": field_key,
            "type": field_type_ref,
            "typeHref": field_type_href,
            "hasTypeVariable": False,
            "position": None,
            "modifiers": get_modifiers(field_elem),
            "ignore": False,
            "classOrInterfaceKey": owner_key
        }
    return fields


# ─── Extraction: Method Parameters ───────────────────────────────────────────

def extract_method_parameters(method_elem, method_key):
    """Extract non-return parameters from a method/operation."""
    parameters = []
    for param_elem in method_elem.findall(".//ownedParameter", NS):
        direction = param_elem.attrib.get('direction')
        signature = param_elem.attrib.get('signature')
        if signature:
            continue
        if direction == "return":
            continue
        param_name = get_name(param_elem)
        if param_name is None:
            continue
        parameters.append({
            "name": param_name,
            "key": get_elem_id(param_elem),
            "type": param_elem.attrib.get('type'),
            "hasTypeVariable": False,
            "position": None,
            "modifiers": get_modifiers(param_elem),
            "ignore": False,
            "methodKey": method_key
        })
    return parameters


# ─── Extraction: Methods (ownedOperation) ────────────────────────────────────

def extract_methods(elem, owner_key):
    """Extract ownedOperation elements (methods) from a classifier."""
    methods = {}
    for method_elem in elem.findall(".//ownedOperation", NS):
        method_name = get_name(method_elem)
        if method_name is None:
            continue
        method_key = get_elem_id(method_elem)

        # Extract return type
        return_type = None
        for param_elem in method_elem.findall(".//ownedParameter", NS):
            if param_elem.attrib.get('direction') == 'return':
                return_type = param_elem.attrib.get('type')
                break

        methods[method_name] = {
            "name": method_name,
            "key": method_key,
            "type": None,
            "hasTypeVariable": False,
            "position": None,
            "modifiers": get_modifiers(method_elem),
            "overrideAnnotation": False,
            "returnType": return_type,
            "parameters": extract_method_parameters(method_elem, method_key),
            "classOrInterfaceKey": owner_key
        }
    return methods


# ─── Extraction: Class ───────────────────────────────────────────────────────

def extract_classes(root, generalizations, realizations):
    """Extract all uml:Class elements. Backward-compatible output format."""
    classes = {}
    for elem in find_elements_by_type(root, 'uml:Class'):
        class_name = get_name(elem)
        if class_name is None:
            continue
        class_key = get_elem_id(elem)

        file_path = safe_file_name(class_name)
        if file_path == ".":
            file_path = safe_file_name(class_key)

        classes[class_name] = {
            # from AstElementTypeContext
            "name": class_name,
            "key": class_key,
            "type": "class",
            "hasTypeVariable": False,
            "position": None,
            # From ClassOrInterfaceTypeContext
            "modifiers": get_modifiers(elem),
            "fields": extract_fields(elem, class_key),
            "methods": extract_methods(elem, class_key),
            "file_path": "./" + file_path,
            "anonymous": False,
            "auxclass": False,
            "implements_": realizations.get(class_key, []),
            "extends_": generalizations.get(class_key, []),
            "definedInClassOrInterfaceTypeKey": None,
            "innerDefinedClasses": {},
            "innerDefinedInterfaces": {}
        }
    return classes


# ─── Extraction: Interface ───────────────────────────────────────────────────

def extract_interfaces(root, generalizations):
    """Extract all uml:Interface elements."""
    interfaces = {}
    for elem in find_elements_by_type(root, 'uml:Interface'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        interfaces[name] = {
            "name": name,
            "key": key,
            "type": "interface",
            "hasTypeVariable": False,
            "position": None,
            "modifiers": get_modifiers(elem),
            "fields": extract_fields(elem, key),
            "methods": extract_methods(elem, key),
            "file_path": "./" + safe_file_name(name),
            "extends_": generalizations.get(key, []),
        }
    return interfaces


# ─── Extraction: Enumeration ─────────────────────────────────────────────────

def extract_enumerations(root):
    """Extract all uml:Enumeration elements."""
    enums = {}
    for elem in find_elements_by_type(root, 'uml:Enumeration'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        literals = []
        for lit_elem in elem.findall(".//ownedLiteral"):
            lit_name = get_name(lit_elem)
            if lit_name:
                literals.append({
                    "name": lit_name,
                    "key": get_elem_id(lit_elem),
                })

        enums[name] = {
            "name": name,
            "key": key,
            "type": "enumeration",
            "modifiers": get_modifiers(elem),
            "literals": literals,
            "fields": extract_fields(elem, key),
            "methods": extract_methods(elem, key),
            "file_path": "./enum_" + safe_file_name(name),
        }
    return enums


# ─── Extraction: DataType ────────────────────────────────────────────────────

def extract_datatypes(root):
    """Extract all uml:DataType elements."""
    datatypes = {}
    for elem in find_elements_by_type(root, 'uml:DataType'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        datatypes[name] = {
            "name": name,
            "key": key,
            "type": "dataType",
            "modifiers": get_modifiers(elem),
            "fields": extract_fields(elem, key),
            "methods": extract_methods(elem, key),
            "file_path": "./datatype_" + safe_file_name(name),
        }
    return datatypes


# ─── Extraction: Association ─────────────────────────────────────────────────

def extract_associations(root):
    """Extract all uml:Association and uml:AssociationClass elements."""
    associations = {}
    for uml_type in ('uml:Association', 'uml:AssociationClass'):
        for elem in find_elements_by_type(root, uml_type):
            key = get_elem_id(elem)
            name = get_name(elem) or key
            if not name:
                continue

            member_end_refs = elem.attrib.get('memberEnd', '').split()
            navigable_end_refs = elem.attrib.get('navigableOwnedEnd', '').split()

            owned_ends = []
            for end_elem in elem.findall(".//ownedEnd", NS):
                end_type = end_elem.attrib.get('type')
                end_name = get_name(end_elem)

                lower = None
                upper = None
                lower_elem = end_elem.find("lowerValue")
                upper_elem = end_elem.find("upperValue")
                if lower_elem is not None:
                    lower = lower_elem.attrib.get('value', '0')
                if upper_elem is not None:
                    upper = upper_elem.attrib.get('value', '*')

                owned_ends.append({
                    "key": get_elem_id(end_elem),
                    "name": end_name,
                    "type": end_type,
                    "lowerValue": lower,
                    "upperValue": upper,
                    "isNavigable": get_elem_id(end_elem) in navigable_end_refs,
                })

            assoc_type = ("association" if uml_type == 'uml:Association'
                          else "associationClass")

            associations[name] = {
                "name": name,
                "key": key,
                "type": assoc_type,
                "memberEndRefs": member_end_refs,
                "ownedEnds": owned_ends,
                "file_path": "./association_" + safe_file_name(key or name),
            }
    return associations


# ─── Extraction: Dependency / Usage ──────────────────────────────────────────

def extract_dependencies(root):
    """Extract all uml:Dependency and uml:Usage elements."""
    deps = {}
    for uml_type in ('uml:Dependency', 'uml:Usage'):
        for elem in find_elements_by_type(root, uml_type):
            key = get_elem_id(elem)
            name = get_name(elem) or key
            if not name:
                continue

            client = elem.attrib.get('client', '').split()
            supplier = elem.attrib.get('supplier', '').split()
            dep_type = ("dependency" if uml_type == 'uml:Dependency'
                        else "usage")

            deps[key or name] = {
                "name": name,
                "key": key,
                "type": dep_type,
                "clients": client,
                "suppliers": supplier,
                "file_path": f"./{dep_type}_{safe_file_name(key or name)}",
            }
    return deps


# ─── Extraction: Component ───────────────────────────────────────────────────

def extract_components(root, generalizations):
    """Extract all uml:Component elements."""
    components = {}
    for elem in find_elements_by_type(root, 'uml:Component'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        provided = []
        for real_elem in elem.findall(".//interfaceRealization"):
            contract = real_elem.attrib.get('contract')
            if contract:
                provided.append(contract)

        components[name] = {
            "name": name,
            "key": key,
            "type": "component",
            "modifiers": get_modifiers(elem),
            "fields": extract_fields(elem, key),
            "methods": extract_methods(elem, key),
            "providedInterfaces": provided,
            "extends_": generalizations.get(key, []),
            "file_path": "./component_" + safe_file_name(name),
        }
    return components


# ─── Extraction: Deployment Nodes ────────────────────────────────────────────

def extract_deployment_nodes(root):
    """Extract uml:Node, uml:Device, uml:ExecutionEnvironment elements."""
    nodes = {}
    for uml_type in ('uml:Node', 'uml:Device', 'uml:ExecutionEnvironment'):
        for elem in find_elements_by_type(root, uml_type):
            name = get_name(elem)
            if name is None:
                continue
            key = get_elem_id(elem)
            node_type_name = uml_type.split(':')[1].lower()

            nodes[name] = {
                "name": name,
                "key": key,
                "type": node_type_name,
                "modifiers": get_modifiers(elem),
                "fields": extract_fields(elem, key),
                "file_path": f"./node_{safe_file_name(name)}",
            }
    return nodes


# ─── Extraction: UseCase ─────────────────────────────────────────────────────

def extract_usecases(root):
    """Extract all uml:UseCase elements with include/extend relationships."""
    usecases = {}
    for elem in find_elements_by_type(root, 'uml:UseCase'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        includes = []
        for inc_elem in elem.findall(".//include"):
            addition = inc_elem.attrib.get('addition')
            if addition:
                includes.append({
                    "key": get_elem_id(inc_elem),
                    "addition": addition,
                })

        extends = []
        for ext_elem in elem.findall(".//extend"):
            extended_case = ext_elem.attrib.get('extendedCase')
            if extended_case:
                extension_points = []
                for ep_elem in ext_elem.findall(".//extensionPoint"):
                    ep_name = get_name(ep_elem)
                    if ep_name:
                        extension_points.append(ep_name)
                extends.append({
                    "key": get_elem_id(ext_elem),
                    "extendedCase": extended_case,
                    "extensionPoints": extension_points,
                })

        extension_points = []
        for ep_elem in elem.findall("extensionPoint"):
            ep_name = get_name(ep_elem)
            if ep_name:
                extension_points.append({
                    "name": ep_name,
                    "key": get_elem_id(ep_elem),
                })

        owned_usecases = []
        for ouc_elem in elem.findall("ownedUseCase"):
            ouc_name = get_name(ouc_elem)
            if ouc_name:
                owned_usecases.append({
                    "name": ouc_name,
                    "key": get_elem_id(ouc_elem),
                })

        usecases[name] = {
            "name": name,
            "key": key,
            "type": "useCase",
            "modifiers": get_modifiers(elem),
            "includes": includes,
            "extends": extends,
            "extensionPoints": extension_points,
            "ownedUseCases": owned_usecases,
            "file_path": "./usecase_" + safe_file_name(name),
        }
    return usecases


# ─── Extraction: Actor ───────────────────────────────────────────────────────

def extract_actors(root):
    """Extract all uml:Actor elements."""
    actors = {}
    for elem in find_elements_by_type(root, 'uml:Actor'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        actors[name] = {
            "name": name,
            "key": key,
            "type": "actor",
            "modifiers": get_modifiers(elem),
            "file_path": "./actor_" + safe_file_name(name),
        }
    return actors


# ─── Extraction: InstanceSpecification ────────────────────────────────────────

def extract_instances(root):
    """Extract all uml:InstanceSpecification elements."""
    instances = {}
    for elem in find_elements_by_type(root, 'uml:InstanceSpecification'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)
        classifier = elem.attrib.get('classifier')

        slots = []
        for slot_elem in elem.findall(".//slot"):
            defining_feature = slot_elem.attrib.get('definingFeature')
            value_elem = slot_elem.find("value")
            value = None
            if value_elem is not None:
                value = (value_elem.attrib.get('value')
                         or value_elem.attrib.get('instance'))
            slots.append({
                "key": get_elem_id(slot_elem),
                "definingFeature": defining_feature,
                "value": value,
            })

        instances[name] = {
            "name": name,
            "key": key,
            "type": "instanceSpecification",
            "classifier": classifier,
            "slots": slots,
            "file_path": "./instance_" + safe_file_name(name),
        }
    return instances


# ─── Extraction: Package (top-level) ─────────────────────────────────────────

def extract_packages(root):
    """Extract top-level uml:Package elements."""
    packages = {}
    for elem in find_elements_by_type(root, 'uml:Package'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        nested_types = defaultdict(int)
        for child in elem:
            child_type = get_elem_type(child)
            if child_type:
                nested_types[child_type] += 1

        packages[name] = {
            "name": name,
            "key": key,
            "type": "package",
            "nestedElementCounts": dict(nested_types),
            "file_path": "./package_" + safe_file_name(name),
        }
    return packages


# ─── Extraction: Interaction (Sequence Diagram) ──────────────────────────────

def extract_interactions(root):
    """Extract all uml:Interaction elements with lifelines, messages, fragments."""
    interactions = {}
    for elem in find_elements_by_type(root, 'uml:Interaction'):
        name = get_name(elem) or "Interaction"
        key = get_elem_id(elem)

        # Extract lifelines
        lifelines = []
        for ll_elem in elem.findall("lifeline"):
            ll_name = get_name(ll_elem)
            covered_by_str = ll_elem.attrib.get('coveredBy', '')
            lifelines.append({
                "name": ll_name,
                "key": get_elem_id(ll_elem),
                "represents": ll_elem.attrib.get('represents'),
                "coveredBy": (covered_by_str.split()
                              if covered_by_str else []),
            })

        # Extract messages
        messages = []
        for msg_elem in elem.findall("message"):
            msg_name = get_name(msg_elem)
            messages.append({
                "name": msg_name,
                "key": get_elem_id(msg_elem),
                "messageSort": msg_elem.attrib.get('messageSort', 'synchCall'),
                "sendEvent": msg_elem.attrib.get('sendEvent'),
                "receiveEvent": msg_elem.attrib.get('receiveEvent'),
                "connector": msg_elem.attrib.get('connector'),
                "signature": msg_elem.attrib.get('signature'),
            })

        # Extract fragments
        fragments = []
        for frag_elem in elem.findall("fragment"):
            frag_type = get_elem_type(frag_elem)
            frag_data = {
                "key": get_elem_id(frag_elem),
                "type": frag_type,
                "name": get_name(frag_elem),
                "covered": frag_elem.attrib.get('covered'),
                "enclosingInteraction": frag_elem.attrib.get(
                    'enclosingInteraction'),
            }

            if frag_type == 'uml:CombinedFragment':
                frag_data['interactionOperator'] = frag_elem.attrib.get(
                    'interactionOperator', 'seq')
                operands = []
                for op_elem in frag_elem.findall("operand"):
                    guard_elem = op_elem.find("guard")
                    guard_spec = None
                    if guard_elem is not None:
                        spec_elem = guard_elem.find("specification")
                        if spec_elem is not None:
                            guard_spec = spec_elem.attrib.get('value')
                    operands.append({
                        "key": get_elem_id(op_elem),
                        "guard": guard_spec,
                    })
                frag_data['operands'] = operands

            if frag_type == 'uml:BehaviorExecutionSpecification':
                frag_data['start'] = frag_elem.attrib.get('start')
                frag_data['finish'] = frag_elem.attrib.get('finish')

            if frag_type in ('uml:MessageOccurrenceSpecification',
                             'uml:ExecutionOccurrenceSpecification'):
                frag_data['message'] = frag_elem.attrib.get('message')
                frag_data['execution'] = frag_elem.attrib.get('execution')

            fragments.append(frag_data)

        # Extract general orderings
        general_orderings = []
        for go_elem in elem.findall(".//generalOrdering"):
            general_orderings.append({
                "key": get_elem_id(go_elem),
                "before": go_elem.attrib.get('before'),
                "after": go_elem.attrib.get('after'),
            })

        # Extract nested collaborations
        collaborations = []
        for coll_elem in elem.findall("nestedClassifier"):
            coll_type = get_elem_type(coll_elem)
            if coll_type == 'uml:Collaboration':
                coll_name = get_name(coll_elem)
                roles = []
                for attr_elem in coll_elem.findall("ownedAttribute", NS):
                    roles.append({
                        "name": get_name(attr_elem),
                        "key": get_elem_id(attr_elem),
                        "type": attr_elem.attrib.get('type'),
                    })
                collaborations.append({
                    "name": coll_name,
                    "key": get_elem_id(coll_elem),
                    "roles": roles,
                })

        interactions[name] = {
            "name": name,
            "key": key,
            "type": "interaction",
            "lifelines": lifelines,
            "messages": messages,
            "fragments": fragments,
            "generalOrderings": general_orderings,
            "collaborations": collaborations,
            "lifelineCount": len(lifelines),
            "messageCount": len(messages),
            "fragmentCount": len(fragments),
            "file_path": "./interaction_" + safe_file_name(name),
        }
    return interactions


# ─── Extraction: Activity ────────────────────────────────────────────────────

def extract_activities(root):
    """Extract all uml:Activity elements with nodes, edges, partitions."""
    activities = {}
    for elem in find_elements_by_type(root, 'uml:Activity'):
        name = get_name(elem) or "Activity"
        key = get_elem_id(elem)

        # Extract nodes
        nodes = []
        for node_elem in elem.findall("node"):
            node_type = get_elem_type(node_elem)
            node_name = get_name(node_elem)
            incoming_str = node_elem.attrib.get('incoming', '')
            outgoing_str = node_elem.attrib.get('outgoing', '')

            node_data = {
                "name": node_name,
                "key": get_elem_id(node_elem),
                "nodeType": node_type,
                "inPartition": node_elem.attrib.get('inPartition'),
                "incoming": (incoming_str.split()
                             if incoming_str else []),
                "outgoing": (outgoing_str.split()
                             if outgoing_str else []),
            }

            # For OpaqueAction, extract body content
            if node_type == 'uml:OpaqueAction':
                body_elems = node_elem.findall("body")
                if body_elems:
                    node_data['body'] = [b.text for b in body_elems
                                         if b.text]

            # For SendSignalAction, extract signal info
            if node_type == 'uml:SendSignalAction':
                signal = node_elem.attrib.get('signal')
                if signal:
                    node_data['signal'] = signal

            # For CallBehaviorAction, extract behavior reference
            if node_type == 'uml:CallBehaviorAction':
                behavior = node_elem.attrib.get('behavior')
                if behavior:
                    node_data['behavior'] = behavior

            nodes.append(node_data)

        # Extract edges
        edges = []
        for edge_elem in elem.findall("edge"):
            edge_type = get_elem_type(edge_elem)
            edge_data = {
                "name": get_name(edge_elem),
                "key": get_elem_id(edge_elem),
                "edgeType": edge_type,
                "source": edge_elem.attrib.get('source'),
                "target": edge_elem.attrib.get('target'),
            }

            guard_elem = edge_elem.find("guard")
            if guard_elem is not None:
                guard_type = get_elem_type(guard_elem)
                if guard_type == 'uml:LiteralString':
                    edge_data['guard'] = guard_elem.attrib.get('value')
                else:
                    body_elem = guard_elem.find("body")
                    spec_elem = guard_elem.find("specification")
                    if body_elem is not None and body_elem.text:
                        edge_data['guard'] = body_elem.text
                    elif spec_elem is not None:
                        edge_data['guard'] = spec_elem.attrib.get('value')

            edges.append(edge_data)

        # Extract partitions (swimlanes)
        partitions = []
        for group_elem in elem.findall("group"):
            group_type = get_elem_type(group_elem)
            if group_type == 'uml:ActivityPartition':
                part_name = get_name(group_elem)
                partition_nodes_str = group_elem.attrib.get('node', '')
                partitions.append({
                    "name": part_name,
                    "key": get_elem_id(group_elem),
                    "nodeRefs": (partition_nodes_str.split()
                                 if partition_nodes_str else []),
                })

        node_type_counts = defaultdict(int)
        for n in nodes:
            node_type_counts[n['nodeType'] or 'unknown'] += 1

        activities[name] = {
            "name": name,
            "key": key,
            "type": "activity",
            "nodes": nodes,
            "edges": edges,
            "partitions": partitions,
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "partitionCount": len(partitions),
            "nodeTypeCounts": dict(node_type_counts),
            "file_path": "./activity_" + safe_file_name(name),
        }
    return activities


# ─── Extraction: StateMachine ────────────────────────────────────────────────

def extract_statemachines(root):
    """Extract all uml:StateMachine elements with regions, states, transitions."""
    statemachines = {}
    for elem in find_elements_by_type(root, 'uml:StateMachine'):
        name = get_name(elem) or "StateMachine"
        key = get_elem_id(elem)

        regions = []
        for region_elem in elem.findall("region"):
            region_key = get_elem_id(region_elem)
            region_name = get_name(region_elem)

            # Extract states (subvertices)
            states = []
            for sv_elem in region_elem.findall("subvertex"):
                sv_type = get_elem_type(sv_elem)
                sv_name = get_name(sv_elem)
                state_data = {
                    "name": sv_name,
                    "key": get_elem_id(sv_elem),
                    "stateType": sv_type,
                }

                if sv_type == 'uml:Pseudostate':
                    state_data['kind'] = sv_elem.attrib.get('kind',
                                                            'initial')

                nested_regions = sv_elem.findall("region")
                if nested_regions:
                    state_data['isComposite'] = True
                    state_data['nestedRegionCount'] = len(nested_regions)

                entry = sv_elem.find("entry")
                exit_ = sv_elem.find("exit")
                do_activity = sv_elem.find("doActivity")
                if entry is not None:
                    state_data['entry'] = (get_name(entry)
                                           or get_elem_type(entry))
                if exit_ is not None:
                    state_data['exit'] = (get_name(exit_)
                                          or get_elem_type(exit_))
                if do_activity is not None:
                    state_data['doActivity'] = (get_name(do_activity)
                                                or get_elem_type(do_activity))

                states.append(state_data)

            # Extract transitions
            transitions = []
            for trans_elem in region_elem.findall("transition"):
                trans_name = get_name(trans_elem)
                trans_data = {
                    "name": trans_name,
                    "key": get_elem_id(trans_elem),
                    "source": trans_elem.attrib.get('source'),
                    "target": trans_elem.attrib.get('target'),
                }

                guard_elem = trans_elem.find("ownedRule")
                if guard_elem is not None:
                    spec_elem = guard_elem.find("specification")
                    if spec_elem is not None:
                        trans_data['guard'] = spec_elem.attrib.get('value')

                trigger_elem = trans_elem.find("trigger")
                if trigger_elem is not None:
                    trans_data['trigger'] = get_name(trigger_elem)
                    trans_data['triggerEvent'] = trigger_elem.attrib.get(
                        'event')

                effect_elem = trans_elem.find("effect")
                if effect_elem is not None:
                    trans_data['effect'] = (get_name(effect_elem)
                                            or get_elem_type(effect_elem))

                transitions.append(trans_data)

            regions.append({
                "name": region_name,
                "key": region_key,
                "states": states,
                "transitions": transitions,
                "stateCount": len(states),
                "transitionCount": len(transitions),
            })

        statemachines[name] = {
            "name": name,
            "key": key,
            "type": "stateMachine",
            "regions": regions,
            "totalStates": sum(r['stateCount'] for r in regions),
            "totalTransitions": sum(r['transitionCount'] for r in regions),
            "file_path": "./statemachine_" + safe_file_name(name),
        }
    return statemachines


# ─── Extraction: Collaboration (standalone, Communication Diagram) ────────────

def extract_collaborations(root):
    """Extract standalone uml:Collaboration elements (not nested in Interactions)."""
    collaborations = {}
    for elem in find_elements_by_type(root, 'uml:Collaboration'):
        name = get_name(elem)
        if name is None:
            continue
        key = get_elem_id(elem)

        roles = []
        for attr_elem in elem.findall("ownedAttribute", NS):
            roles.append({
                "name": get_name(attr_elem),
                "key": get_elem_id(attr_elem),
                "type": attr_elem.attrib.get('type'),
            })

        collaborations[name] = {
            "name": name,
            "key": key,
            "type": "collaboration",
            "roles": roles,
            "file_path": "./collaboration_" + safe_file_name(name),
        }
    return collaborations


# ─── Extraction: InformationFlow / CommunicationPath ─────────────────────────

def extract_information_flows(root):
    """Extract uml:InformationFlow and uml:CommunicationPath elements."""
    flows = {}
    for uml_type in ('uml:InformationFlow', 'uml:CommunicationPath'):
        for elem in find_elements_by_type(root, uml_type):
            key = get_elem_id(elem)
            name = get_name(elem) or key
            if not name:
                continue

            flow_type = ("informationFlow"
                         if uml_type == 'uml:InformationFlow'
                         else "communicationPath")
            flow_data = {
                "name": name,
                "key": key,
                "type": flow_type,
            }

            if uml_type == 'uml:InformationFlow':
                flow_data['informationSource'] = elem.attrib.get(
                    'informationSource', '').split()
                flow_data['informationTarget'] = elem.attrib.get(
                    'informationTarget', '').split()
                flow_data['conveyed'] = elem.attrib.get(
                    'conveyed', '').split()
            else:
                member_end_refs = elem.attrib.get('memberEnd', '').split()
                flow_data['memberEndRefs'] = member_end_refs

            flow_data['file_path'] = (
                f"./{flow_type}_{safe_file_name(key or name)}")
            flows[name] = flow_data
    return flows


# ─── Main Extraction Orchestrator ─────────────────────────────────────────────

def extract_all_uml_elements(xmi_content):
    """Parse XMI content and extract ALL UML element types.

    Returns:
        all_elements (dict): Category -> {name -> details} mapping
        diagram_info (dict): Metadata about the diagram
        error (str|None): Error message if parsing failed
    """
    try:
        tree = ET.ElementTree(ET.fromstring(xmi_content))
        root = tree.getroot()
    except ET.ParseError as e:
        return None, None, str(e)

    # Detect what's in the diagram
    type_counts = detect_diagram_types(root)
    classification = classify_diagram(type_counts)

    # Pre-compute shared lookups
    generalizations = extract_generalizations(root)
    realizations = extract_interface_realizations(root)

    # Extract all element types
    all_elements = {}

    # --- Structural elements ---
    classes = extract_classes(root, generalizations, realizations)
    if classes:
        all_elements['classes'] = classes

    interfaces = extract_interfaces(root, generalizations)
    if interfaces:
        all_elements['interfaces'] = interfaces

    enumerations = extract_enumerations(root)
    if enumerations:
        all_elements['enumerations'] = enumerations

    datatypes = extract_datatypes(root)
    if datatypes:
        all_elements['dataTypes'] = datatypes

    associations = extract_associations(root)
    if associations:
        all_elements['associations'] = associations

    dependencies = extract_dependencies(root)
    if dependencies:
        all_elements['dependencies'] = dependencies

    components = extract_components(root, generalizations)
    if components:
        all_elements['components'] = components

    deployment_nodes = extract_deployment_nodes(root)
    if deployment_nodes:
        all_elements['deploymentNodes'] = deployment_nodes

    packages = extract_packages(root)
    if packages:
        all_elements['packages'] = packages

    instances = extract_instances(root)
    if instances:
        all_elements['instanceSpecifications'] = instances

    info_flows = extract_information_flows(root)
    if info_flows:
        all_elements['informationFlows'] = info_flows

    # --- Behavioral elements ---
    interactions = extract_interactions(root)
    if interactions:
        all_elements['interactions'] = interactions

    activities = extract_activities(root)
    if activities:
        all_elements['activities'] = activities

    statemachines = extract_statemachines(root)
    if statemachines:
        all_elements['stateMachines'] = statemachines

    usecases = extract_usecases(root)
    if usecases:
        all_elements['useCases'] = usecases

    actors = extract_actors(root)
    if actors:
        all_elements['actors'] = actors

    collaborations = extract_collaborations(root)
    if collaborations:
        all_elements['collaborations'] = collaborations

    # Build diagram info
    diagram_info = {
        "classification": classification,
        "detectedTypes": type_counts,
        "elementCounts": {cat: len(elems)
                          for cat, elems in all_elements.items()},
        "totalElements": sum(len(elems) for elems in all_elements.values()),
    }

    return all_elements, diagram_info, None


# ─── File Writing ─────────────────────────────────────────────────────────────

def write_element_files(all_elements, output_directory):
    """Write individual JSON files for each extracted element.

    Returns:
        written (int): Number of files successfully written
        errors (list): List of error messages
    """
    written = 0
    errors = []

    for category, elements in all_elements.items():
        for elem_name, details in elements.items():
            file_path_base = details.get("file_path", f"./{elem_name}")
            file_path = os.path.join(output_directory,
                                     f"{file_path_base}.json")

            try:
                parent_dir = os.path.dirname(file_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                with open(file_path, 'w') as f:
                    json.dump(details, f, indent=4)
                written += 1
            except Exception as e:
                errors.append(f"  {file_path}: {e}")

    return written, errors


# ─── process_folder ───────────────────────────────────────────────────────────

def process_folder(path_to_folder, output_folder):
    """Process all XMI files in the input folder, extract all UML elements."""

    if os.path.exists(output_folder):
        print(f"Output folder '{output_folder}' already exists.")
        print("Will merge/overwrite existing data. "
              "To start fresh, delete it first.")
    os.makedirs(output_folder, exist_ok=True)

    # Counters
    total_files = 0
    processed_files = 0
    total_elements_written = 0
    successful_diagrams = 0
    skipped_empty = 0
    parse_errors = 0

    diagram_type_counts = defaultdict(int)
    class_diagram_count = 0
    non_class_diagram_count = 0

    start_time = time.time()
    errors_list = []

    if not os.path.exists(path_to_folder) or not os.path.isdir(path_to_folder):
        print(f"{path_to_folder} is not a valid directory")
        return

    all_xmi_files = sorted([f for f in os.listdir(path_to_folder)
                            if f.endswith(".xmi")])
    total_files = len(all_xmi_files)
    print(f"Found {total_files} XMI files to process")

    for filename in all_xmi_files:
        processed_files += 1
        filepath = os.path.join(path_to_folder, filename)

        try:
            with open(filepath, 'rb') as file:
                raw_content = file.read()
                content = raw_content.decode('utf-8', errors='replace')
        except Exception as e:
            errors_list.append(f"Read error - {filename}: {e}")
            parse_errors += 1
            continue

        # Extract diagram ID from filename
        diagram_id = (filename[:-4]
                      if filename.endswith('.xmi') else filename)

        all_elements, diagram_info, error = extract_all_uml_elements(content)

        if error:
            errors_list.append(f"Parse error - {filename}: {error}")
            parse_errors += 1
            continue

        if not all_elements or diagram_info['totalElements'] == 0:
            skipped_empty += 1
            continue

        # Update classification counters
        classification = diagram_info['classification']
        for cat in classification['categories']:
            diagram_type_counts[cat] += 1
        if classification['is_class_diagram']:
            class_diagram_count += 1
        else:
            non_class_diagram_count += 1

        # Create output directory for this diagram
        output_dir = os.path.join(output_folder, diagram_id)
        os.makedirs(output_dir, exist_ok=True)

        diagram_info['diagram_id'] = diagram_id
        diagram_info['source_file'] = filename
        error_in_diagram = False

        try:
            with open(os.path.join(output_dir,
                                   '_diagram_info.json'), 'w') as f:
                json.dump(diagram_info, f, indent=4)
        except Exception as e:
            errors_list.append(
                f"DiagramInfo write error - {filename}: {e}")
            error_in_diagram = True

        written, write_errors = write_element_files(
            all_elements, output_dir)
        total_elements_written += written

        if write_errors:
            errors_list.extend(
                [f"{filename}: {we}" for we in write_errors])
            error_in_diagram = True

        if not error_in_diagram:
            successful_diagrams += 1
        else:
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)

        # Progress reporting
        elapsed = time.time() - start_time
        if processed_files > 1:
            est_total = elapsed / processed_files * total_files
            time_left = max(0.0, est_total - elapsed)
            cat_str = ",".join(classification['categories'])
            print(
                f"[{processed_files}/{total_files}] {diagram_id} "
                f"[{cat_str}] {written} elements | "
                f"Total: {total_elements_written} | "
                f"ETA: {format_time(time_left)} | "
                f"Elapsed: {format_time(elapsed)}"
            )
        elif processed_files == 1:
            print(
                f"[{processed_files}/{total_files}] {diagram_id} "
                f"{written} elements | "
                f"Elapsed: {format_time(elapsed)}"
            )

    # Print summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Total XMI files:         {total_files}")
    print(f"Processed:               {processed_files}")
    print(f"Successful diagrams:     {successful_diagrams}")
    print(f"Skipped (empty):         {skipped_empty}")
    print(f"Parse errors:            {parse_errors}")
    print(f"Total elements written:  {total_elements_written}")
    print(f"Class diagrams:          {class_diagram_count}")
    print(f"Non-class diagrams:      {non_class_diagram_count}")
    print(f"Time elapsed:            {format_time(elapsed)}")
    print()
    print("Diagram type breakdown:")
    for dtype, count in sorted(diagram_type_counts.items(),
                               key=lambda x: -x[1]):
        print(f"  {dtype}: {count}")

    if errors_list:
        print(f"\n{len(errors_list)} errors encountered:")
        for err in errors_list[:20]:
            print(f"  {err}")
        if len(errors_list) > 20:
            print(f"  ... and {len(errors_list) - 20} more")

    # Write global summary JSON
    summary = {
        "totalXmiFiles": total_files,
        "processedFiles": processed_files,
        "successfulDiagrams": successful_diagrams,
        "skippedEmpty": skipped_empty,
        "parseErrors": parse_errors,
        "totalElementsWritten": total_elements_written,
        "classDiagramCount": class_diagram_count,
        "nonClassDiagramCount": non_class_diagram_count,
        "diagramTypeBreakdown": dict(diagram_type_counts),
        "elapsedSeconds": elapsed,
        "errors": errors_list[:100],
    }
    summary_path = os.path.join(output_folder, '_extraction_summary.json')
    try:
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\nSummary written to: {summary_path}")
    except Exception as e:
        print(f"Failed to write summary: {e}")

    print("Finished")


# ─── Behavioral Diagram Extraction from Classification JSON ───────────────────

BEHAVIORAL_TARGET_TYPES = {'Sequence', 'StateMachine', 'Activity',
                           'Communication', 'Timing'}


def extract_behavioral_diagrams(classification_json_path, output_json_path):
    """Extract behavioral diagrams (Sequence, StateMachine, Activity,
    Communication, Timing) from the classification JSON and write
    an updated UML_Behavioral_Diagrams_Extracted.json.

    Two extraction categories:
      1. primary_behavioral_diagrams: diagrams whose primary 'uml.type'
         is one of the target behavioral types.
      2. score_signal_behavioral_diagrams: diagrams NOT primarily behavioral
         but which have score signals for any target behavioral type.
    """
    print(f"Loading classification JSON: {classification_json_path}")
    with open(classification_json_path, 'r') as f:
        data = json.load(f)

    by_diagram = data.get('GroupedClassJSON', {}).get('by_diagram', [])
    total_source = len(by_diagram)
    print(f"Total source diagrams: {total_source}")

    # ── Category 1: Primary behavioral ──
    primary = []
    for entry in by_diagram:
        uml = entry.get('uml', {})
        if uml.get('type') in BEHAVIORAL_TARGET_TYPES:
            primary.append(entry)

    # ── Category 2: Score-signal behavioral ──
    score_signal = []
    for entry in by_diagram:
        uml = entry.get('uml', {})
        if uml.get('type') in BEHAVIORAL_TARGET_TYPES:
            continue  # already in primary
        score = uml.get('score', {})
        for bt in BEHAVIORAL_TARGET_TYPES:
            if bt in score and score[bt] > 0:
                score_signal.append(entry)
                break

    # ── Breakdown ──
    from collections import Counter
    primary_breakdown = Counter()
    for e in primary:
        primary_breakdown[e['uml']['type']] += 1

    score_signal_breakdown = Counter()
    for e in score_signal:
        score = e['uml'].get('score', {})
        for bt in BEHAVIORAL_TARGET_TYPES:
            if bt in score and score[bt] > 0:
                score_signal_breakdown[bt] += 1

    total_primary = len(primary)
    total_score_signal = len(score_signal)
    total_combined = total_primary + total_score_signal

    print(f"\nExtraction Results:")
    print(f"  Primary behavioral diagrams: {total_primary}")
    for t, c in primary_breakdown.most_common():
        print(f"    {t}: {c}")
    print(f"  Score-signal behavioral diagrams: {total_score_signal}")
    for t, c in score_signal_breakdown.most_common():
        print(f"    {t}: {c} (diagrams with this score signal)")
    print(f"  Combined total: {total_combined}")

    # ── Build output JSON ──
    output = {
        "metadata": {
            "description": (
                "Behavioral UML Diagrams extracted for AKG Research: "
                "Sequence, State Machine, Activity, Communication, "
                "and Timing diagrams"
            ),
            "source_file": os.path.basename(classification_json_path),
            "source_dataset": "4_Extracted-All-UML-Informations",
            "extraction_criteria": (
                f"uml.type IN {{{', '.join(sorted(BEHAVIORAL_TARGET_TYPES))}}}"
                f" (primary classification)"
            ),
            "target_diagram_types": sorted(BEHAVIORAL_TARGET_TYPES),
            "total_source_diagrams": total_source,
            "total_extracted_primary": total_primary,
            "total_extracted_score_signal": total_score_signal,
            "total_extracted_combined": total_combined,
            "breakdown_by_type_primary": dict(
                primary_breakdown.most_common()),
            "breakdown_score_signal_types": dict(
                score_signal_breakdown.most_common()),
            "extraction_timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%S%z"),
        },
        "primary_behavioral_diagrams": primary,
        "score_signal_behavioral_diagrams": score_signal,
    }

    print(f"\nWriting output to: {output_json_path}")
    # Ensure parent directory exists
    parent_dir = os.path.dirname(output_json_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(output_json_path, 'w') as f:
        json.dump(output, f, indent=2)

    file_size_mb = os.path.getsize(output_json_path) / (1024 * 1024)
    print(f"Output written: {output_json_path} ({file_size_mb:.1f} MB)")
    print("Behavioral extraction complete.")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract ALL types of UML diagram elements from XMI files "
            "OR extract behavioral diagrams from classification JSON "
            "(enhanced version of 3_extract_uml_information.py)."
        )
    )
    subparsers = parser.add_subparsers(dest='command', help='Sub-command')

    # ── Subcommand: extract-xmi ──
    xmi_parser = subparsers.add_parser(
        'extract-xmi',
        help='Extract all UML elements from XMI files')
    xmi_parser.add_argument(
        "path_to_folder", type=str,
        help=("Path to the folder containing the XMI files "
              "(e.g., ../1_UML-Diagrams/1_UML-Diagrams)")
    )
    xmi_parser.add_argument(
        "--output_folder", type=str,
        default="./4_Extracted-All-UML-Informations",
        help=("Path to the output folder "
              "(default: ./4_Extracted-All-UML-Informations)")
    )

    # ── Subcommand: extract-behavioral ──
    beh_parser = subparsers.add_parser(
        'extract-behavioral',
        help=('Extract behavioral diagrams (Sequence, StateMachine, '
              'Activity, Communication, Timing) from classification JSON'))
    beh_parser.add_argument(
        "classification_json", type=str,
        help=("Path to the classification JSON file "
              "(e.g., UML_All_Diagram_Classification_Extraction_Latest.json)")
    )
    beh_parser.add_argument(
        "--output_json", type=str,
        default="./UML_Behavioral_Diagrams_Extracted.json",
        help=("Path to the output behavioral JSON file "
              "(default: ./UML_Behavioral_Diagrams_Extracted.json)")
    )

    args = parser.parse_args()

    if args.command == 'extract-xmi':
        process_folder(args.path_to_folder, args.output_folder)
    elif args.command == 'extract-behavioral':
        extract_behavioral_diagrams(
            args.classification_json, args.output_json)
    else:
        # Backward compatibility: if no subcommand, treat first arg as folder
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            # Legacy mode: positional arg is path_to_folder
            legacy_parser = argparse.ArgumentParser()
            legacy_parser.add_argument("path_to_folder", type=str)
            legacy_parser.add_argument(
                "--output_folder", type=str,
                default="./4_Extracted-All-UML-Informations")
            legacy_args = legacy_parser.parse_args()
            process_folder(legacy_args.path_to_folder,
                           legacy_args.output_folder)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
