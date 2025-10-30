#!/usr/bin/env python3

import os
import httpx
from fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("name-resolver", version="0.1.0")

# Create HTTP client for API calls
httpx_client = httpx.AsyncClient()
BASE_URL = os.getenv("NAME_RESOLVER_URL", "https://name-resolution-sri.renci.org")


@mcp.tool()
async def lookup(
    query: str,
    limit: int = 10,
    offset: int = 0,
    autocomplete: bool = False,
    highlighting: bool = False,
    biolink_type: str | None = None,
    only_prefixes: list[str] | None = None,
    exclude_prefixes: list[str] | None = None,
    only_taxa: list[str] | None = None,
    return_json: bool = False
) -> str | list[dict]:
    """Search for biological entities by name with filtering options

    Args:
        query: Search term
        limit: Maximum number of results (default: 10)
        offset: Number of results to skip for pagination (default: 0)
        autocomplete: Enable autocomplete/partial matching (default: false)
        highlighting: Enable search term highlighting (default: false)
        biolink_type: Filter by Biolink entity type (e.g., 'Disease', 'ChemicalEntity', 'Gene')
        only_prefixes: Only include results from these namespaces (e.g., ['MONDO', 'CHEBI', 'HGNC'])
        exclude_prefixes: Exclude results from these namespaces
        only_taxa: Only include results from these taxa (e.g., ['NCBITaxon:9606'] for humans)
        return_json: Return raw JSON instead of formatted string (default: false)
    """
    # Build parameters
    params = [
        ("string", query),
        ("limit", str(limit)),
        ("offset", str(offset)),
        ("autocomplete", "true" if autocomplete else "false"),
        ("highlighting", "true" if highlighting else "false")
    ]

    if biolink_type:
        params.append(("biolink_type", biolink_type))

    for prefix in (only_prefixes or []):
        params.append(("only_prefixes", prefix))

    for prefix in (exclude_prefixes or []):
        params.append(("exclude_prefixes", prefix))

    for taxon in (only_taxa or []):
        params.append(("only_taxa", taxon))

    response = await httpx_client.get(
        f"{BASE_URL}/lookup",
        params=params
    )
    response.raise_for_status()
    results = response.json()

    # Return raw JSON if requested
    if return_json:
        return results

    # Build response text
    filter_info = []
    if biolink_type:
        filter_info.append(f"type: {biolink_type}")
    if only_prefixes:
        filter_info.append(f"prefixes: {', '.join(only_prefixes)}")
    if exclude_prefixes:
        filter_info.append(f"excluding: {', '.join(exclude_prefixes)}")
    if only_taxa:
        filter_info.append(f"taxa: {', '.join(only_taxa)}")

    filter_text = f" ({'; '.join(filter_info)})" if filter_info else ""

    text = f"Found {len(results)} results for '{query}'{filter_text}:\n\n"

    for i, result in enumerate(results, 1):
        label = result.get("label", result.get("name", "Unknown"))
        curie = result.get("curie", "Unknown")
        biolink = result.get("biolink_type", "")

        text += f"{i}. **{label}** ({curie})"
        if biolink:
            text += f" [{biolink}]"
        text += "\n"

        # Show synonyms if available
        synonyms = result.get("synonyms", [])
        if synonyms:
            text += f"   Synonyms: {', '.join(synonyms[:3])}"
            if len(synonyms) > 3:
                text += f" (+{len(synonyms)-3} more)"
            text += "\n"
        text += "\n"

    if offset > 0:
        text += f"\n(Showing results {offset+1}-{offset+len(results)})"

    return text


@mcp.tool()
async def synonyms(curies: list[str], return_json: bool = False) -> str | dict:
    """Get synonyms for biological entity CURIEs

    Args:
        curies: List of CURIEs to get synonyms for (e.g., ['CHEBI:5931', 'MONDO:0007739'])
        return_json: Return raw JSON instead of formatted string (default: false)
    """
    if not curies:
        raise ValueError("No CURIEs provided")

    # Format the curies parameter correctly for the API
    params = []
    for curie in curies:
        params.append(("preferred_curies", curie))

    response = await httpx_client.get(
        f"{BASE_URL}/synonyms",
        params=params
    )
    response.raise_for_status()
    results = response.json()

    # Return raw JSON if requested
    if return_json:
        return results

    text = f"Synonyms for {len(curies)} CURIE(s):\n\n"
    for curie in curies:
        curie_data = results.get(curie, {})
        if curie_data and "names" in curie_data:
            synonyms_list = curie_data["names"]
            preferred_name = curie_data.get("preferred_name", "Unknown")
            text += f"**{curie}** ({preferred_name}): {len(synonyms_list)} synonyms\n"
            # Show first 5 synonyms
            for synonym in synonyms_list[:5]:
                text += f"  - {synonym}\n"
            if len(synonyms_list) > 5:
                text += f"  ... and {len(synonyms_list) - 5} more\n"
        else:
            text += f"**{curie}:** No synonyms found\n"
        text += "\n"

    return text


def main():
    mcp.run()


if __name__ == "__main__":
    main()