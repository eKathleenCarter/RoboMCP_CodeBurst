#!/usr/bin/env python3

import os
import httpx
from fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("robokop", version="0.1.0")

# Create HTTP client for API calls with longer timeout for large queries
httpx_client = httpx.AsyncClient(timeout=60.0)
BASE_URL = os.getenv("ROBOKOP_URL", "https://automat.renci.org/robokopkg")


def format_edge(edge_wrapper: dict, query_curie: str, index: int) -> str:
    """Format a single edge for display

    Args:
        edge_wrapper: The edge wrapper containing 'edge' and 'adj_node' data
        query_curie: The CURIE that was queried (for context in display)
        index: The edge number for display

    Returns:
        Formatted string representation of the edge
    """
    edge = edge_wrapper.get("edge", edge_wrapper)
    adj_node = edge_wrapper.get("adj_node", {})

    predicate_val = edge.get("predicate", "unknown")
    direction = edge.get("direction", "")
    properties = edge.get("properties", {})

    adj_node_id = adj_node.get("id", "Unknown")
    adj_node_name = adj_node.get("name", "")
    adj_node_categories = adj_node.get("category", [])

    # Clean up biolink prefix
    predicate_display = predicate_val.replace("biolink:", "")

    # Build the edge display line
    text = f"{index}. "

    # Display the edge based on direction
    if direction == "<":
        # Adjacent node points TO the query curie
        text += f"{adj_node_id}"
        if adj_node_name:
            text += f" ({adj_node_name})"
        text += f" --[{predicate_display}]--> {query_curie}\n"
    else:
        # Query curie points TO the adjacent node (or bidirectional)
        text += f"{query_curie} --[{predicate_display}]--> {adj_node_id}"
        if adj_node_name:
            text += f" ({adj_node_name})"
        text += "\n"

    # Show categories if available
    if adj_node_categories:
        cats = adj_node_categories if isinstance(adj_node_categories, list) else [adj_node_categories]
        cats_display = [c.replace("biolink:", "") for c in cats]
        text += f"   Categories: {', '.join(cats_display)}\n"

    # Show direction if available
    if direction:
        text += f"   Direction: {direction}\n"

    # Show knowledge source if available
    knowledge_source = properties.get("primary_knowledge_source", "")
    if knowledge_source:
        source_display = knowledge_source.replace("infores:", "")
        text += f"   Source: {source_display}\n"

    # Show publications if available
    publications = properties.get("publications", [])
    if publications:
        text += f"   Publications: {', '.join(publications[:3])}"
        if len(publications) > 3:
            text += f" (+{len(publications)-3} more)"
        text += "\n"

    # Show any qualifier properties
    qualifiers = {k: v for k, v in properties.items() if "qualifier" in k.lower()}
    if qualifiers:
        for qual_key, qual_value in qualifiers.items():
            # Clean up key name for display
            qual_display = qual_key.replace("_", " ").title()
            if isinstance(qual_value, list):
                text += f"   {qual_display}: {', '.join(str(v) for v in qual_value)}\n"
            else:
                text += f"   {qual_display}: {qual_value}\n"

    # Show sentences if available
    sentences = properties.get("sentences", "")
    if sentences:
        # Sentences can be long, so truncate if needed
        sentence_lines = sentences.split("|")
        for sentence in sentence_lines[:2]:  # Show first 2 sentences
            if sentence.strip() and sentence.strip() != "NA":
                # Truncate very long sentences
                if len(sentence) > 200:
                    sentence = sentence[:200] + "..."
                text += f"   Sentence: {sentence.strip()}\n"

    text += "\n"
    return text


@mcp.tool()
async def get_node(curie: str) -> str:
    """Returns information about a node matching the CURIE identifier

    Args:
        curie: Node identifier (e.g., 'NCBITaxon:7227', 'MONDO:0007739')
    """
    response = await httpx_client.get(
        f"{BASE_URL}/node/{curie}"
    )
    response.raise_for_status()
    result = response.json()

    # Format the response
    if not result:
        return f"No information found for {curie}"

    node_id = result.get("id", curie)
    name = result.get("name", "Unknown")
    categories = result.get("category", [])
    
    text = f"**{node_id}**"
    if name:
        text += f" - {name}\n\n"
    else:
        text += "\n\n"
    
    if categories:
        cat_list = categories if isinstance(categories, list) else [categories]
        text += f"**Categories:** {', '.join(cat_list)}\n"
    
    # Show additional properties if available
    if "description" in result and result["description"]:
        text += f"\n**Description:** {result['description']}\n"
    
    # Show any other relevant fields
    relevant_fields = ["taxon", "iri", "equivalent_identifiers"]
    for field in relevant_fields:
        if field in result and result[field]:
            value = result[field]
            if isinstance(value, list):
                text += f"\n**{field.replace('_', ' ').title()}:** {', '.join(str(v) for v in value[:5])}"
                if len(value) > 5:
                    text += f" (+{len(value)-5} more)"
                text += "\n"
            else:
                text += f"\n**{field.replace('_', ' ').title()}:** {value}\n"

    return text


@mcp.tool()
async def get_edges(
    curie: str,
    category: str | None = None,
    predicate: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    count_only: bool = False
) -> str:
    """Returns edges connected to a node

    Args:
        curie: Node identifier (e.g., 'NCBITaxon:7227')
        category: Filter adjacent nodes by category (optional)
        predicate: Filter edges by predicate (optional)
        limit: Limit number of results (optional)
        offset: Pagination offset (optional)
        count_only: Return only count of edges (optional, default: False)
    """
    params = {}
    if category:
        params["category"] = category
    if predicate:
        params["predicate"] = predicate
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if count_only:
        params["count_only"] = "true"

    response = await httpx_client.get(
        f"{BASE_URL}/edges/{curie}",
        params=params
    )
    response.raise_for_status()
    results = response.json()

    # Handle the actual API response format: {"query_curie": "...", "edges": [...]}
    query_curie = results.get("query_curie", curie)
    edges = results.get("edges", results if isinstance(results, list) else [results])

    # Handle count_only response
    if count_only:
        count = len(edges) if isinstance(edges, list) else edges
        filters = []
        if category:
            filters.append(f"category: {category}")
        if predicate:
            filters.append(f"predicate: {predicate}")
        filter_text = f" ({'; '.join(filters)})" if filters else ""
        return f"Found {count} edges for {query_curie}{filter_text}"

    # Format edge results
    if not edges:
        return f"No edges found for {query_curie}"

    filter_info = []
    if category:
        filter_info.append(f"category: {category}")
    if predicate:
        filter_info.append(f"predicate: {predicate}")
    filter_text = f" ({'; '.join(filter_info)})" if filter_info else ""

    text = f"Found {len(edges)} edge(s) for {query_curie}{filter_text}:\n\n"

    for i, edge_wrapper in enumerate(edges[:20], 1):  # Limit display to 20
        text += format_edge(edge_wrapper, query_curie, i)

    if len(edges) > 20:
        text += f"\n(Showing first 20 of {len(edges)} edges. Use limit/offset for pagination)"

    return text


@mcp.tool()
async def get_edge_summary(curie: str) -> str:
    """Returns a summary of edge types connected to a node

    Args:
        curie: Node identifier (e.g., 'NCBITaxon:7227')
    """
    response = await httpx_client.get(
        f"{BASE_URL}/edge_summary/{curie}"
    )
    response.raise_for_status()
    results = response.json()

    if not results:
        return f"No edge summary found for {curie}"

    # Handle the actual API response format: {"query_curie": "...", "edge_types": [...]}
    query_curie = results.get("query_curie", curie)
    edge_types = results.get("edge_types", results)

    text = f"Edge summary for {query_curie}:\n\n"

    # edge_types is a list of dicts with predicate, category, count
    if isinstance(edge_types, list):
        # Sort by count (descending)
        sorted_results = sorted(edge_types, key=lambda x: x.get("count", 0), reverse=True)

        for item in sorted_results:
            predicate_val = item.get("predicate", "unknown")
            node_category = item.get("category", "unknown")
            count = item.get("count", 0)

            # Clean up biolink prefixes for readability
            predicate_display = predicate_val.replace("biolink:", "")
            category_display = node_category.replace("biolink:", "")

            text += f"- **{predicate_display}** → {category_display}: {count} edge(s)\n"

    return text


@mcp.tool()
async def get_edges_between(curie1: str, curie2: str) -> str:
    """Find all edges connecting two nodes

    This function queries both nodes to find their edge counts, then retrieves edges
    from the node with fewer connections and filters for edges connecting to the other node.

    Args:
        curie1: First node identifier (e.g., 'MONDO:0016098')
        curie2: Second node identifier (e.g., 'DRUGBANK:DB01024')
    """
    # Get edge summaries for both nodes to determine which has fewer edges
    response1 = await httpx_client.get(f"{BASE_URL}/edge_summary/{curie1}")
    response1.raise_for_status()
    summary1 = response1.json()

    response2 = await httpx_client.get(f"{BASE_URL}/edge_summary/{curie2}")
    response2.raise_for_status()
    summary2 = response2.json()

    # Calculate total edge counts
    edge_types1 = summary1.get("edge_types", [])
    edge_types2 = summary2.get("edge_types", [])

    count1 = sum(item.get("count", 0) for item in edge_types1)
    count2 = sum(item.get("count", 0) for item in edge_types2)

    # Query the node with fewer edges
    if count1 <= count2:
        query_curie = curie1
        target_curie = curie2
        query_count = count1
    else:
        query_curie = curie2
        target_curie = curie1
        query_count = count2

    # Get all edges for the query node
    response = await httpx_client.get(
        f"{BASE_URL}/edges/{query_curie}",
        params={"limit": 10000}  # Get all edges
    )
    response.raise_for_status()
    results = response.json()

    edges = results.get("edges", [])

    # Filter for edges that connect to the target curie
    connecting_edges = []
    for edge_wrapper in edges:
        adj_node = edge_wrapper.get("adj_node", {})
        adj_node_id = adj_node.get("id", "")

        # Check if the adjacent node matches the target curie
        if adj_node_id == target_curie:
            connecting_edges.append(edge_wrapper)

    # Format results
    if not connecting_edges:
        return f"No edges found between {curie1} and {curie2}"

    text = f"Found {len(connecting_edges)} edge(s) connecting {curie1} and {curie2}:\n"
    text += f"(Queried {query_curie} which has {query_count} total edges)\n\n"

    for i, edge_wrapper in enumerate(connecting_edges, 1):
        text += format_edge(edge_wrapper, query_curie, i)

    return text


def main():
    mcp.run()


if __name__ == "__main__":
    main()
