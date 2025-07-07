#!/usr/bin/env python3
"""
Simple MCP Server for Claude Desktop

Uses the proven working server approach from our integration tests.
Clean, no emojis, no stdout interference.
"""

from mcp_server.server import FinancialIntelligenceServer
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path FIRST
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# NOW import the working server (after path setup)

# Configure minimal logging to stderr only
logging.basicConfig(
    level=logging.ERROR,  # Only show errors
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)


def main():
    """Run MCP server for Claude Desktop."""
    try:
        # Create server instance (this works from our tests)
        server = FinancialIntelligenceServer()

        # Run the server
        asyncio.run(server.run())

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
