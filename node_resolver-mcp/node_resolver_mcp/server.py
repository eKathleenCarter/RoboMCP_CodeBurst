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

class NodeProperty(TypedDict):
    property: str
    type: str
    description: str
@mcp.tool()
def get_node_properties_for_class(class_name: str) -> List[NodeProperty]:
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
    # Step 1: Name Resolution - Get CURIEs
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
        return ['biolink:NamedThing']

    # Extract CURIEs
    curies = [result.get("curie") for result in lookup_results if result.get("curie")]

    if not curies:
        return ['biolink:NamedThing']

    # Step 2: Node Normalization - Get Biolink types
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

    if not unique_types:
        return ['biolink:NamedThing']

    # Step 3: Find most specific types using BMT
    most_specific = []
    for biolink_type in unique_types:
        is_most_specific = True
        for other in unique_types:
            if other != biolink_type:
                # Get ancestors with reflexive=True (includes the type itself)
                ancestors = toolkit.get_ancestors(other, reflexive=True, formatted=True, mixin=True)
                if ancestors and f"biolink:{biolink_type}" in ancestors:
                    # biolink_type is an ancestor of other, so it's not most specific
                    is_most_specific = False
                    break
        if is_most_specific:
            most_specific.append(f"biolink:{biolink_type}")

    # Return sorted list, or last type if none found
    return sorted(most_specific) if most_specific else [unique_types[-1]]


def main():
    mcp.run()


if __name__ == "__main__":
    main()
