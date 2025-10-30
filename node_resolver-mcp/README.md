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

- `find_most_specific_type_for_entity` - Find the most specific Biolink type(s) for a biological entity by orchestrating name resolution, normalization, and type hierarchy analysis

### Example Usage

```python
# Find the most specific type for "diabetes"
find_most_specific_type_for_entity("diabetes")
# Returns: ['biolink:Disease']

# Find the most specific type for a gene
find_most_specific_type_for_entity("BRCA1")
# Returns: ['biolink:Gene']
```

## How It Works

This server orchestrates three steps:

1. **Name Resolution** - Searches for the entity name and retrieves CURIEs
2. **Node Normalization** - Gets Biolink types for those CURIEs
3. **Type Filtering** - Uses the Biolink Model Toolkit to find the most specific types in the hierarchy

## License

MIT License - see the [main repository](https://github.com/cbizon/RoboMCP) for details.
