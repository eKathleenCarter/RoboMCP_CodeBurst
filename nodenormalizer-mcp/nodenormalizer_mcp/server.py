#!/usr/bin/env python3

import os
import httpx
from fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("nodenormalizer", version="0.1.0")

# Create HTTP client for API calls
httpx_client = httpx.AsyncClient()
BASE_URL = os.getenv("NODE_NORMALIZER_URL", "https://nodenormalization-sri.renci.org")


@mcp.tool()
async def get_normalized_nodes(
    curies: list[str],
    conflate: bool = True,
    drug_chemical_conflate: bool = True,
    description: bool = False,
    show_types: bool = True,
    show_information_content: bool = True,
    return_json: bool = False
) -> str | dict:
    """Normalize biological entity CURIEs and apply conflation

    Args:
        curies: List of CURIEs to normalize (e.g., ['MESH:D014867', 'NCIT:C34373'])
        conflate: Whether to apply gene/protein conflation (default: true)
        drug_chemical_conflate: Whether to apply drug/chemical conflation (default: true)
        description: Whether to return CURIE descriptions when possible (default: false)
        show_types: Whether to show biolink types (default: true)
        show_information_content: Whether to show information content (default: true)
        return_json: Return raw JSON instead of formatted string (default: false)
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
        ("individual_types", "false")
    ])

    response = await httpx_client.get(
        f"{BASE_URL}/get_normalized_nodes",
        params=params
    )
    response.raise_for_status()
    results = response.json()

    # Return raw JSON if requested
    if return_json:
        return results

    # Build response text
    text = f"Normalized {len(curies)} CURIE(s):\n\n"

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

            # Show biolink type if requested
            if show_types:
                type_info = node_data.get("type", [])
                if type_info:
                    if isinstance(type_info, list):
                        type_str = ", ".join(type_info)
                    else:
                        type_str = type_info
                    text += f"   Type: {type_str}\n"

            # Show information content if requested and available
            if show_information_content:
                info_content = node_data.get("information_content")
                if info_content is not None:
                    text += f"   Information Content: {info_content}\n"

            # Show description if requested and available
            if description and "description" in node_data.get("id", {}):
                desc = node_data["id"]["description"]
                if desc:
                    text += f"   Description: {desc}\n"

            # Show ALL equivalent identifiers
            equivalent_ids = node_data.get("equivalent_identifiers", [])
            if equivalent_ids and len(equivalent_ids) > 1:
                other_ids = [eq["identifier"] for eq in equivalent_ids if eq["identifier"] != normalized_id]
                if other_ids:
                    text += f"   Equivalent IDs ({len(other_ids)}): {', '.join(other_ids)}\n"

            text += "\n"
        else:
            text += f"**{curie}:** Not found in response\n\n"

    return text


def main():
    mcp.run()


if __name__ == "__main__":
    main()