#!/usr/bin/env python3
"""
Simple MCP Server for Claude Desktop

Direct approach like the working integration test - no complex path setup.
"""

import asyncio
import sys
import logging
from mcp_server.server import FinancialIntelligenceServer

# Configure minimal logging to stderr only
logging.basicConfig(
    level=logging.ERROR,
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
