# RoboMCP

A collection of Model Context Protocol (MCP) servers providing AI assistants with access to biomedical knowledge APIs from the Translator and ROBOKOP ecosystem.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables AI assistants like Claude to securely connect to external data sources and tools. These MCP servers act as bridges between Claude and specialized biomedical knowledge services.

## Available Servers

### Name Resolver MCP
Provides biological entity name lookup and synonym resolution.

**Tools:**
- `lookup` - Search for biological entities by name with filtering options
  - Filter by entity type (Disease, Gene, ChemicalEntity, etc.)
  - Restrict to specific namespaces (MONDO, CHEBI, HGNC, etc.)
  - Filter by taxa (e.g., human-only results)
  - Autocomplete and highlighting support

- `synonyms` - Get all known synonyms for biological entity CURIEs
  - Returns preferred names and alternative labels
  - Useful for entity disambiguation

### Node Normalizer MCP
Provides biological entity CURIE normalization and conflation.

**Tools:**
- `get_normalized_nodes` - Normalize biological entity CURIEs
  - Maps identifiers to canonical forms
  - Finds equivalent identifiers across namespaces
  - Optional gene/protein conflation
  - Optional drug/chemical conflation
  - Returns descriptions and type information

## Installation

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install a Server

Each server can be installed independently:

```bash
# Name Resolver
cd name-resolver-mcp
uv sync

# Node Normalizer
cd nodenormalizer-mcp
uv sync
```

## Usage with Claude Desktop

### Configure Claude Desktop

Add the servers to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "name-resolver": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/RoboMCP/name-resolver-mcp",
        "python",
        "run_server.py"
      ]
    },
    "nodenormalizer": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/RoboMCP/nodenormalizer-mcp",
        "python",
        "run_server.py"
      ]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/RoboMCP` with the actual absolute path to your RoboMCP directory.

### Restart Claude Desktop

After updating the configuration, restart Claude Desktop for the changes to take effect.

## Example Usage

Once configured, you can ask Claude questions like:

**Name Resolution:**
- "Look up 'diabetes' in the name resolver"
- "Find all genes with 'BRCA' in the name, limited to human genes"
- "Get synonyms for MONDO:0007739"

**Node Normalization:**
- "Normalize these CURIEs: MESH:D014867, NCIT:C34373"
- "What are the equivalent identifiers for CHEBI:5931?"
- "Normalize UniProtKB:P04637 with gene/protein conflation enabled"

## API Endpoints

These servers connect to:
- **Name Resolver**: https://name-resolution-sri-dev.apps.renci.org
- **Node Normalizer**: https://nodenormalization-sri.renci.org

## Development

See [CLAUDE.md](CLAUDE.md) for development instructions.

## License

[Add license information]

## Contributing

[Add contribution guidelines]

## Support

For issues or questions, please open an issue on the [GitHub repository](https://github.com/cbizon/RoboMCP).
