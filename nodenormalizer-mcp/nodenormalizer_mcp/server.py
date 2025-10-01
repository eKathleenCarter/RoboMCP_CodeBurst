#!/usr/bin/env python3

import httpx
from fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("nodenormalizer", version="0.1.0")

# Create HTTP client for API calls
httpx_client = httpx.AsyncClient()
BASE_URL = "https://nodenormalization-sri.renci.org"


@mcp.tool()
async def get_normalized_nodes(
    curies: list[str],
    conflate: bool = True,
    drug_chemical_conflate: bool = True,
    description: bool = False,
    individual_types: bool = False
) -> str:
    """Normalize biological entity CURIEs and apply conflation

    Args:
        curies: List of CURIEs to normalize (e.g., ['MESH:D014867', 'NCIT:C34373'])
        conflate: Whether to apply gene/protein conflation (default: true)
        drug_chemical_conflate: Whether to apply drug/chemical conflation (default: true)
        description: Whether to return CURIE descriptions when possible (default: false)
        individual_types: Whether to return individual types for equivalent identifiers (default: false)
    """
    if not curies:
        raise ValueError("No CURIEs provided")

    # Build parameters for GET request
    params = []
    for curie in curies:
        params.append(("curie", curie))

    params.extend([
        ("conflate", "true" if conflate else "false"),
        ("drug_chemical_conflate", "true" if drug_chemical_conflate else "false"),
        ("description", "true" if description else "false"),
        ("individual_types", "true" if individual_types else "false")
    ])

    response = await httpx_client.get(
        f"{BASE_URL}/get_normalized_nodes",
        params=params
    )
    response.raise_for_status()
    results = response.json()

    # Build response text
    settings_info = []
    if conflate:
        settings_info.append("gene/protein conflation: ON")
    if drug_chemical_conflate:
        settings_info.append("drug/chemical conflation: ON")
    if description:
        settings_info.append("descriptions: ON")
    if individual_types:
        settings_info.append("individual types: ON")

    settings_text = f" ({'; '.join(settings_info)})" if settings_info else ""

    text = f"Normalized {len(curies)} CURIE(s){settings_text}:\n\n"

    for curie in curies:
        if curie in results:
            node_data = results[curie]
            if node_data is None:
                text += f"**{curie}:** Not found\n\n"
                continue

            # Get the normalized identifier
            normalized_id = node_data.get("id", {}).get("identifier", "Unknown")
            label = node_data.get("id", {}).get("label", "")

            text += f"**{curie}** → **{normalized_id}**"
            if label:
                text += f" ({label})"
            text += "\n"

            # Show description if requested and available
            if description and "description" in node_data.get("id", {}):
                desc = node_data["id"]["description"]
                if desc:
                    text += f"   Description: {desc}\n"

            # Show equivalent identifiers
            equivalent_ids = node_data.get("equivalent_identifiers", [])
            if equivalent_ids and len(equivalent_ids) > 1:
                other_ids = [eq["identifier"] for eq in equivalent_ids if eq["identifier"] != normalized_id]
                if other_ids:
                    text += f"   Equivalent IDs: {', '.join(other_ids[:5])}"
                    if len(other_ids) > 5:
                        text += f" (+{len(other_ids)-5} more)"
                    text += "\n"

            # Show individual types if requested
            if individual_types and equivalent_ids:
                types_found = set()
                for eq in equivalent_ids:
                    if "type" in eq:
                        if isinstance(eq["type"], list):
                            types_found.update(eq["type"])
                        else:
                            types_found.add(eq["type"])
                if types_found:
                    text += f"   Types: {', '.join(sorted(types_found))}\n"

            text += "\n"
        else:
            text += f"**{curie}:** Not found in response\n\n"

    return text


def main():
    mcp.run()


if __name__ == "__main__":
    main()