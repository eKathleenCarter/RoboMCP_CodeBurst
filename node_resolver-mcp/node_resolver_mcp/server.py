#!/usr/bin/env python3

import os
import httpx
from typing import List
from fastmcp import FastMCP
from bmt import Toolkit
import itertools
from typing_extensions import TypedDict

# Create the FastMCP server
mcp = FastMCP("node-resolver", version="0.1.0")

# Create HTTP client for API calls
httpx_client = httpx.AsyncClient()
NAME_RESOLVER_URL = os.getenv("NAME_RESOLVER_URL", "https://name-resolution-sri.renci.org")
NODE_NORMALIZER_URL = os.getenv("NODE_NORMALIZER_URL", "https://nodenormalization-sri.renci.org")

# Initialize BMT toolkit
biolink_version = os.getenv("BIOLINK_VERSION")
toolkit = Toolkit(biolink_version) if biolink_version else Toolkit()

# class NodeProperty(TypedDict):
#     property: str
#     type: str
#     description: str
@mcp.tool()
def get_node_properties_for_class(class_name: str):
    ancestors = toolkit.get_ancestors(class_name)

    all_slots = toolkit.get_all_slots()
    slots_without_domain = [s for s in all_slots if len(toolkit.get_slot_domain(s)) == 0 and toolkit.is_node_property(s)]

    slots_nested = [toolkit.get_all_slots_with_class_domain(a) for a in ancestors]
    slots_from_class = set(s for sl in slots_nested for s in sl)

    slots_with_domain = [s for s in slots_from_class if toolkit.is_node_property(s)]

    output = []
    for s in itertools.chain(slots_with_domain, slots_without_domain):
        value_type = toolkit.get_value_type_for_slot(s)
        type = toolkit.view.get_type(value_type)
        primative_type = type.typeof or value_type

        output.append({
            "property": s,
            "type": primative_type,
            "description": type.description,
        })
    return output

@mcp.tool()
async def resolve_entity_to_curies(
    entity: str,
    limit: int = 5,
    biolink_type: str | None = None,
    only_prefixes: list[str] | None = None
) -> List[str]:
    """Resolve a biological entity name to CURIEs using the Name Resolution Service

    Args:
        entity: Biological entity name (e.g., "diabetes", "BRCA1", "aspirin")
        limit: Number of results to return (default: 5)
        biolink_type: Filter by Biolink entity type (e.g., 'Disease', 'Gene')
        only_prefixes: Only include results from these namespaces (e.g., ['MONDO', 'HGNC'])

    Returns:
        List of CURIEs for the entity
    """
    params = [
        ("string", entity),
        ("limit", str(limit)),
        ("autocomplete", "false"),
        ("highlighting", "false")
    ]

    if biolink_type:
        params.append(("biolink_type", biolink_type))

    for prefix in (only_prefixes or []):
        params.append(("only_prefixes", prefix))

    response = await httpx_client.get(
        f"{NAME_RESOLVER_URL}/lookup",
        params=params
    )
    response.raise_for_status()
    lookup_results = response.json()

    if not lookup_results:
        return []

    # Extract CURIEs
    curies = [result.get("curie") for result in lookup_results if result.get("curie")]
    return curies


@mcp.tool()
async def get_types_for_curies(curies: List[str]) -> List[str]:
    """Get Biolink types for a list of CURIEs using the Node Normalization Service

    Args:
        curies: List of CURIEs (e.g., ['MONDO:0005148', 'HGNC:1100'])

    Returns:
        List of unique Biolink types for the CURIEs
    """
    if not curies:
        return []

    norm_params = []
    for curie in curies:
        norm_params.append(("curie", curie))
    norm_params.extend([
        ("conflate", "true"),
        ("drug_chemical_conflate", "true"),
        ("description", "false"),
        ("individual_types", "false")
    ])

    response = await httpx_client.get(
        f"{NODE_NORMALIZER_URL}/get_normalized_nodes",
        params=norm_params
    )
    response.raise_for_status()
    norm_data = response.json()

    # Collect all Biolink types
    all_types = []
    for curie in curies:
        if curie in norm_data and norm_data[curie]:
            node_info = norm_data[curie]
            if "type" in node_info:
                types = node_info["type"]
                if isinstance(types, list):
                    all_types.extend(types)
                else:
                    all_types.append(types)

    # Remove duplicates
    unique_types = list(set(all_types))
    return unique_types


@mcp.tool()
def find_most_specific_types(types: List[str]) -> List[str]:
    """Find the most specific Biolink types from a list using the Biolink Model Toolkit

    Given a list of Biolink types, returns only the most specific ones by filtering
    out any that are ancestors of other types in the list.

    Args:
        types: List of Biolink types (e.g., ['biolink:Disease', 'biolink:NamedThing'])

    Returns:
        List of most specific Biolink types, sorted alphabetically
    """
    if not types:
        return ['biolink:NamedThing']

    most_specific = []
    for biolink_type in types:
        is_most_specific = True
        for other in types:
            if other != biolink_type:
                # Get ancestors with reflexive=True (includes the type itself)
                ancestors = toolkit.get_ancestors(other, reflexive=True, formatted=True, mixin=True)
                if ancestors and biolink_type in ancestors:
                    # biolink_type is an ancestor of other, so it's not most specific
                    is_most_specific = False
                    break
        if is_most_specific:
            most_specific.append(biolink_type)

    # Return sorted list, or last type if none found
    return sorted(most_specific) if most_specific else [types[-1]]


@mcp.tool()
async def find_most_specific_type_for_entity(
    entity: str,
    limit: int = 5,
    biolink_type: str | None = None,
    only_prefixes: list[str] | None = None
) -> List[str]:
    """Find the most specific Biolink type(s) for a biological entity

    This tool orchestrates three steps:
    1. Name Resolution - Search for the entity and get CURIEs
    2. Node Normalization - Get Biolink types for those CURIEs
    3. Type Filtering - Find the most specific types in the hierarchy

    Args:
        entity: Biological entity name (e.g., "diabetes", "BRCA1", "aspirin")
        limit: Number of name resolution results to consider (default: 5)
        biolink_type: Filter by Biolink entity type during name resolution
        only_prefixes: Only include results from these namespaces (e.g., ['MONDO', 'HGNC'])

    Returns:
        List of most specific Biolink type(s) for the entity

    Examples:
        >>> find_most_specific_type_for_entity("diabetes")
        ['biolink:Disease']

        >>> find_most_specific_type_for_entity("BRCA1")
        ['biolink:Gene']
    """
    # Step 1: Resolve entity to CURIEs
    curies = await resolve_entity_to_curies.fn(entity, limit, biolink_type, only_prefixes)

    if not curies:
        return ['biolink:NamedThing']

    # Step 2: Get Biolink types for CURIEs
    types = await get_types_for_curies.fn(curies)

    if not types:
        return ['biolink:NamedThing']

    # Step 3: Find most specific types
    most_specific = find_most_specific_types.fn(types)

    return most_specific


@mcp.tool()
async def enrich_node_from_row(
    row_data: dict,
    name_column: str = "name",
    limit: int = 1,
    biolink_type: str | None = None,
    only_prefixes: list[str] | None = None
) -> dict:
    """Enrich a node from a CSV row by mapping available data to valid Biolink properties

    This tool performs a complete workflow:
    1. Extract entity name from the row
    2. Resolve name to CURIE
    3. Determine most specific Biolink type
    4. Get valid properties for that type
    5. Map CSV columns to those properties where data exists

    Args:
        row_data: Dictionary representing a CSV row (column_name: value)
        name_column: Name of the column containing the entity name (default: "name")
        limit: Number of CURIE candidates to consider (default: 1)
        biolink_type: Filter by Biolink entity type during name resolution
        only_prefixes: Only include results from these namespaces

    Returns:
        Dictionary with:
        - entity: Original entity name
        - curie: Best matching CURIE
        - type: Most specific Biolink type
        - properties: Valid properties for this type
        - mapped_data: CSV columns mapped to properties with values

    Examples:
        >>> row = {"name": "aspirin", "Description": "pain reliever", "CAS ID": "50-78-2"}
        >>> enrich_node_from_row(row)
        {
            "entity": "aspirin",
            "curie": "CHEBI:15365",
            "type": "biolink:SmallMolecule",
            "properties": [...],
            "mapped_data": {
                "description": {"csv_column": "Description", "value": "pain reliever"},
                "has_identifier": {"csv_column": "CAS ID", "value": "50-78-2"}
            }
        }
    """
    # Step 1: Extract entity name
    entity = row_data.get(name_column)
    if not entity:
        return {
            "error": f"No value found in column '{name_column}'",
            "row_data": row_data
        }

    # Step 2: Resolve entity to CURIEs
    curies = await resolve_entity_to_curies.fn(entity, limit, biolink_type, only_prefixes)

    if not curies:
        return {
            "entity": entity,
            "curie": None,
            "type": "biolink:NamedThing",
            "properties": [],
            "mapped_data": {},
            "error": "No CURIEs found"
        }

    # Use the first (best) CURIE
    best_curie = curies[0]

    # Step 3: Get Biolink types and find most specific
    types = await get_types_for_curies.fn([best_curie])

    if not types:
        return {
            "entity": entity,
            "curie": best_curie,
            "type": "biolink:NamedThing",
            "properties": [],
            "mapped_data": {},
            "error": "No types found"
        }

    most_specific = find_most_specific_types.fn(types)
    best_type = most_specific[0] if most_specific else "biolink:NamedThing"

    # Step 4: Get properties for this type
    clean_type = best_type.replace("biolink:", "")
    properties = get_node_properties_for_class.fn(clean_type)

    # Step 5: Map CSV columns to properties
    mapped_data = {}
    property_names = [prop["property"] for prop in properties]

    # Try to map CSV columns to property names
    for csv_column, value in row_data.items():
        # Skip the name column and empty values
        if csv_column == name_column or not value or value == "":
            continue

        # Normalize column name for matching (lowercase, replace spaces with underscores)
        normalized_column = csv_column.lower().replace(" ", "_").replace("-", "_")

        # Direct match
        if normalized_column in property_names:
            mapped_data[normalized_column] = {
                "csv_column": csv_column,
                "value": value,
                "property_type": next((p["type"] for p in properties if p["property"] == normalized_column), "unknown")
            }
        # Partial/fuzzy matching for common patterns
        else:
            # Description column
            if "description" in normalized_column and "description" in property_names:
                mapped_data["description"] = {
                    "csv_column": csv_column,
                    "value": value,
                    "property_type": next((p["type"] for p in properties if p["property"] == "description"), "unknown")
                }
            # ID columns might map to has_identifier or xref
            elif "id" in normalized_column or "identifier" in normalized_column:
                if "xref" in property_names:
                    mapped_data.setdefault("xref", [])
                    mapped_data["xref"].append({
                        "csv_column": csv_column,
                        "value": value,
                        "property_type": "string"
                    })

    return {
        "entity": entity,
        "curie": best_curie,
        "type": best_type,
        "all_curies": curies,
        "all_types": types,
        "valid_properties": properties,
        "mapped_data": mapped_data,
        "unmapped_columns": [col for col in row_data.keys() if col != name_column and col not in [m.get("csv_column") for m in (mapped_data.values() if isinstance(mapped_data, dict) else [])]]
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
