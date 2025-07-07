#!/usr/bin/env python3
"""
MCP Server for Claude Desktop (Asyncio Compatible)

Handles Claude Desktop's existing event loop without conflicts.
"""

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
    """Run MCP server for Claude Desktop without asyncio conflicts."""
    try:
        # Create server instance
        server = FinancialIntelligenceServer()

        # Don't use asyncio.run() - Claude Desktop manages the event loop
        # Just run the server's async run method directly
        import asyncio

        # Get the current event loop (provided by Claude Desktop)
        try:
            loop = asyncio.get_running_loop()
            # If we have a running loop, create a task
            task = loop.create_task(server.run())
            # This will be handled by Claude Desktop's event loop
            return task
        except RuntimeError:
            # If no running loop, use asyncio.run (fallback)
            asyncio.run(server.run())

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # For MCP protocol, we need to handle the async execution differently
    import asyncio

    try:
        # Check if we're in an existing event loop (Claude Desktop scenario)
        loop = asyncio.get_running_loop()
        # If we reach here, we're in Claude Desktop's loop
        server = FinancialIntelligenceServer()
        # Run the server in the existing loop
        asyncio.create_task(server.run())
    except RuntimeError:
        # No existing loop, run normally
        main()
