#!/usr/bin/env python3

import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from node_resolver_mcp.server import main

if __name__ == "__main__":
    main()
