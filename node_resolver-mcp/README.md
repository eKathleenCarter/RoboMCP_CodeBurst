# Node Resolver MCP

MCP server for orchestrating node resolution, normalization, and type finding across Translator services. This server provides high-level tools that chain multiple biomedical APIs together to answer complex questions about biological entities.

## Documentation

For full documentation, installation instructions, and usage examples, see the main [RoboMCP repository](https://github.com/cbizon/RoboMCP).

## Quick Start

```bash
# Run with uvx (no installation needed)
uvx node-resolver-mcp
```

## Tools

### High-Level Orchestration

- **`find_most_specific_type_for_entity`** - Find the most specific Biolink type(s) for a biological entity by orchestrating all three steps below

### Individual Step Tools

- **`resolve_entity_to_curies`** - Resolve a biological entity name to CURIEs (Step 1)
- **`get_types_for_curies`** - Get Biolink types for a list of CURIEs (Step 2)
- **`find_most_specific_types`** - Find the most specific types from a list of Biolink types (Step 3)

### Additional Tools

- **`get_node_properties_for_class`** - Get all node properties for a Biolink class

### Example Usage

```python
# High-level: Find the most specific type in one call
find_most_specific_type_for_entity("diabetes")
# Returns: ['biolink:Disease']

# Or use individual steps:
# Step 1: Get CURIEs
curies = resolve_entity_to_curies("diabetes")
# Returns: ['MONDO:0005148', 'MESH:D003920', ...]

# Step 2: Get types
types = get_types_for_curies(curies)
# Returns: ['biolink:Disease', 'biolink:NamedThing']

# Step 3: Find most specific
most_specific = find_most_specific_types(types)
# Returns: ['biolink:Disease']
```

## How It Works

This server orchestrates three steps:

1. **Name Resolution** - Searches for the entity name and retrieves CURIEs
2. **Node Normalization** - Gets Biolink types for those CURIEs
3. **Type Filtering** - Uses the Biolink Model Toolkit to find the most specific types in the hierarchy

## License

MIT License - see the [main repository](https://github.com/cbizon/RoboMCP) for details.
