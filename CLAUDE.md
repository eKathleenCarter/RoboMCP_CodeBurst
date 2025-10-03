# RoboMCP

## Goal

We are providing a set of MCP servers to various Translator / ROBOKOP tools. Each server wraps a specific biomedical knowledge API and exposes it through the Model Context Protocol (MCP), making these tools accessible to AI assistants like Claude.

## Project Structure

Each MCP server is in its own subdirectory:
- `name-resolver-mcp/` - Name Resolution Service API wrapper
- `nodenormalizer-mcp/` - Node Normalization Service API wrapper
- `robokop-mcp/` - ROBOKOP Knowledge Graph API wrapper

## Basic Setup

* **github**: This project has a github repo at https://github.com/cbizon/RoboMCP
* **uv**: We are using uv for package and environment management (NOT conda)
* **tests**: We are using pytest, and want to maintain high code coverage
* **FastMCP**: All servers use FastMCP for simplified MCP implementation

## Key Dependencies

- **fastmcp** (>=0.1.0) - MCP server framework
- **httpx** (>=0.24.0) - Async HTTP client for API calls
- **Python** (>=3.10) - Required by the MCP library

## Development Workflow

### Adding a New MCP Server

1. Create a new directory: `mkdir <server-name>-mcp`
2. Create `pyproject.toml` with:
   ```toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "<server-name>-mcp"
   version = "0.1.0"
   description = "MCP server for <Service Name>"
   readme = "README.md"
   license = {text = "MIT"}
   authors = [{name = "Chris Bizon"}]
   requires-python = ">=3.10"
   keywords = ["mcp", "biomedical", "translator", "<relevant-keywords>"]
   classifiers = [
       "Development Status :: 4 - Beta",
       "Intended Audience :: Developers",
       "Intended Audience :: Science/Research",
       "License :: OSI Approved :: MIT License",
       "Programming Language :: Python :: 3",
       "Programming Language :: Python :: 3.10",
       "Programming Language :: Python :: 3.11",
       "Programming Language :: Python :: 3.12",
       "Topic :: Scientific/Engineering :: Bio-Informatics",
   ]
   dependencies = ["fastmcp>=0.1.0", "httpx>=0.24.0"]

   [project.urls]
   Homepage = "https://github.com/cbizon/RoboMCP"
   Repository = "https://github.com/cbizon/RoboMCP"
   Issues = "https://github.com/cbizon/RoboMCP/issues"

   [project.scripts]
   <server-name>-mcp = "<server_name>_mcp.server:main"

   [tool.hatch.build.targets.wheel]
   packages = ["<server_name>_mcp"]
   ```
3. Create package directory: `mkdir <server_name>_mcp`
4. Create `<server_name>_mcp/server.py` using FastMCP:
   ```python
   import os
   from fastmcp import FastMCP
   import httpx

   mcp = FastMCP("<server-name>", version="0.1.0")
   httpx_client = httpx.AsyncClient()
   BASE_URL = os.getenv("<SERVICE>_URL", "https://default-endpoint.example.com")

   @mcp.tool()
   async def my_tool(param: str) -> str:
       """Tool description"""
       # Implementation
       pass

   def main():
       mcp.run()
   ```
5. Create `run_server.py` entry point
6. Create `README.md` for the package (see existing packages for template)
7. Run `uv sync` to install dependencies
8. Create local `claude_config.json` for testing (not committed to git)
9. Write tests in `tests/` directory

### Running a Server Locally

```bash
cd <server-name>-mcp
uv run python run_server.py
```

### Running Tests

```bash
cd <server-name>-mcp
uv run pytest
```

### Adding Dependencies

Edit `pyproject.toml` and add to `dependencies` list, then run:
```bash
uv sync
```

## **RULES OF THE ROAD**

- Don't use mocks. They obscure problems

- Ask clarifying questions

- Don't make classes just to group code. It is non-pythonic and hard to test.

- Do not implement bandaids - treat the root cause of problems

- Don't use try/except as a way to hide problems.  It is often good just to let something fail and figure out why.

- Once we have a test, do not delete it without explicit permission.  

- Do not return made up results if an API fails.  Let it fail.

- When changing code, don't make duplicate functions - just change the function. We can always roll back changes if needed.

- Keep the directories clean, don't leave a bunch of junk laying around.

- When making pull requests, NEVER ever mention a `co-authored-by` or similar aspects. In particular, never mention the tool used to create the commit message or PR.

- Check git status before commits

