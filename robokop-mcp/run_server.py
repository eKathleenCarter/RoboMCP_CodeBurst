#!/usr/bin/env python3

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
from robokop_mcp.server import main

if __name__ == "__main__":
    main()
