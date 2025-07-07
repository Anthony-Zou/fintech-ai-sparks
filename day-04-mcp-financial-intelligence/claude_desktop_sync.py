#!/usr/bin/env python3
"""
Synchronous MCP Server wrapper for Claude Desktop

Avoids all asyncio.run() calls to prevent conflicts with Claude Desktop's event loop.
"""

import sys
import logging

# Configure minimal logging to stderr only
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)


def main():
    """Main entry point that doesn't use asyncio.run()."""
    try:
        # Import and create server without running it
        from mcp_server.server import FinancialIntelligenceServer
        server = FinancialIntelligenceServer()

        # Get the FastMCP instance and let it handle stdio
        mcp = server.mcp

        # This should work with Claude Desktop's stdio without asyncio conflicts
        # The MCP library should handle the event loop internally
        return mcp

    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
