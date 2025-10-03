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

### ROBOKOP MCP
Provides access to the ROBOKOP Knowledge Graph for querying biomedical relationships.

**Tools:**
- `get_node` - Get information about a specific node by CURIE
- `get_edges` - Get edges connected to a node with optional filtering
- `get_edge_summary` - Get a summary of edge types connected to a node
- `get_edges_between` - Find all edges connecting two nodes

## Installation

Each MCP server is published as an independent package on PyPI.

### Recommended: Use with uvx

No installation needed! Use `uvx` to run the servers in isolated environments (see Configuration section below).

### Install in a Virtual Environment

If you prefer to install the packages:

```bash
# Create and activate a virtual environment
python -m venv mcp-env
source mcp-env/bin/activate  # On Windows: mcp-env\Scripts\activate

# Install desired servers
pip install name-resolver-mcp
pip install nodenormalizer-mcp
pip install robokop-mcp
```

### Install from Source for Development

```bash
# Clone the repository
git clone https://github.com/cbizon/RoboMCP.git
cd RoboMCP

# Install a specific server in editable mode
cd name-resolver-mcp
pip install -e .
```

## Configuration

### Environment Variables

Each server can be configured using environment variables to point to different API endpoints:

- `NAME_RESOLVER_URL` - Name Resolution Service endpoint (default: `https://name-resolution-sri.renci.org`)
- `NODE_NORMALIZER_URL` - Node Normalization Service endpoint (default: `https://nodenormalization-sri.renci.org`)
- `ROBOKOP_URL` - ROBOKOP Knowledge Graph endpoint (default: `https://automat.renci.org/robokopkg`)

### Claude Desktop Configuration

Add the servers to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

#### Using uvx (Recommended)

The easiest way to use these servers is with `uvx`, which runs them in isolated environments without installation:

```json
{
  "mcpServers": {
    "name-resolver": {
      "command": "uvx",
      "args": ["name-resolver-mcp"]
    },
    "nodenormalizer": {
      "command": "uvx",
      "args": ["nodenormalizer-mcp"]
    },
    "robokop": {
      "command": "uvx",
      "args": ["robokop-mcp"]
    }
  }
}
```

#### For Local Development

When running from source, use the full uv command:

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
    },
    "robokop": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/RoboMCP/robokop-mcp",
        "python",
        "run_server.py"
      ]
    }
  }
}
```

**Note**: Replace `/absolute/path/to/RoboMCP` with your actual path.

#### Custom API Endpoints

To use custom API endpoints, add environment variables:

```json
{
  "mcpServers": {
    "name-resolver": {
      "command": "name-resolver-mcp",
      "env": {
        "NAME_RESOLVER_URL": "https://your-custom-endpoint.example.com"
      }
    }
  }
}
```

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

## Development

See [CLAUDE.md](CLAUDE.md) for development instructions and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues or questions, please open an issue on the [GitHub repository](https://github.com/cbizon/RoboMCP).
