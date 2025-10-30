import asyncio
import sys

# Add all MCP servers to path
sys.path.insert(0, "name-resolver-mcp")
sys.path.insert(0, "nodenormalizer-mcp")
sys.path.insert(0, "biolink-mcp")

from name_resolver_mcp.server import lookup
from nodenormalizer_mcp.server import get_normalized_nodes
from biolink_mcp.server import find_most_specific_types


async def find_most_specific_type_for_term(search_term: str, limit: int = 5):
    """
    Complete workflow: search term -> CURIEs -> types -> most specific types

    Args:
        search_term: The biological term to search for
        limit: Maximum number of results to process from name resolver
    """
    print("=" * 70)
    print(f"WORKFLOW: Finding most specific type for '{search_term}'")
    print("=" * 70)

    # Step 1: Use Name Resolver to find CURIEs
    print(f"\n📍 STEP 1: Searching for '{search_term}' in Name Resolver...")
    lookup_result = await lookup.fn(query=search_term, limit=limit)
    print(lookup_result)

    # Parse CURIEs from the lookup result (this is a formatted string)
    # In a real MCP client, you'd parse the structured response
    # For this example, we'll manually extract from known results

    # Let's get the raw JSON to extract CURIEs properly
    import httpx
    httpx_client = httpx.AsyncClient()
    response = await httpx_client.get(
        "https://name-resolution-sri.renci.org/lookup",
        params=[("string", search_term), ("limit", str(limit))]
    )
    results = response.json()

    if not results:
        print(f"❌ No results found for '{search_term}'")
        return

    # Extract CURIEs
    curies = [result.get("curie") for result in results if result.get("curie")]
    print(f"\n✅ Found {len(curies)} CURIEs: {curies[:3]}...")

    # Step 2: Use Node Normalizer to get types for each CURIE
    print(f"\n📍 STEP 2: Normalizing CURIEs to get Biolink types...")
    norm_result = await get_normalized_nodes.fn(
        curies=curies,
        show_types=True
    )
    print(norm_result)

    # Extract types from normalized results
    # Parse the formatted string to get types
    # In a real scenario, you'd get the structured data
    response = await httpx_client.get(
        "https://nodenormalization-sri.renci.org/get_normalized_nodes",
        params=[("curie", curie) for curie in curies]
    )
    norm_data = response.json()

    # Collect all types from all CURIEs
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

    # Remove duplicates and clean up formatting
    unique_types = list(set(all_types))

    print(f"\n✅ Found {len(unique_types)} unique Biolink types: {unique_types}")

    # Step 3: Find most specific types
    print(f"\n📍 STEP 3: Finding most specific types...")
    most_specific = find_most_specific_types.fn(unique_types)

    print(f"\n✅ Most specific type(s): {most_specific}")

    return most_specific


async def main():
    """Run examples with different search terms"""

    # Example 1: Search for a disease
    await find_most_specific_type_for_term("diabetes", limit=1)

    print("\n" * 2)

    # Example 2: Search for a gene
    await find_most_specific_type_for_term("BRCA1", limit=1)

    print("\n" * 2)

    # Example 3: Search for a chemical
    await find_most_specific_type_for_term("aspirin", limit=1)


if __name__ == "__main__":
    asyncio.run(main())
