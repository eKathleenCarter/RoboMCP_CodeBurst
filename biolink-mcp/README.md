# Biolink MCP

MCP server for the Biolink Model Toolkit - query and navigate the Biolink Model.

## Documentation

For full documentation, installation instructions, and usage examples, see the main [RoboMCP repository](https://github.com/cbizon/RoboMCP).

## Quick Start

```bash
# Run with uvx (no installation needed)
uvx biolink-mcp
```

## Tools

- `get_element` - Get a Biolink Model element by name
- `get_ancestors` - Get ancestors of a Biolink element
- `get_descendants` - Get descendants of a Biolink element
- `get_all_classes` - Get all Biolink classes
- `get_all_slots` - Get all Biolink slots
- `get_all_entities` - Get all Biolink entities
- `get_element_by_mapping` - Map external CURIEs to Biolink elements
- `is_predicate` - Check if a name is a Biolink predicate
- `get_slot_domain` - Get the domain for a Biolink slot
- `get_slot_range` - Get the range for a Biolink slot

## License

MIT License - see the [main repository](https://github.com/cbizon/RoboMCP) for details.
