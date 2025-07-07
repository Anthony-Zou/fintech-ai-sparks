#!/usr/bin/env python3
"""
MCP Financial Intelligence Server for Claude Desktop

Handles asyncio conflicts by adapting to existing event loops.
"""

import sys
import asyncio
import logging

# Configure minimal logging to stderr only
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)


async def run_server():
    """Run the server in an async context."""
    from mcp_server.server import FinancialIntelligenceServer
    server = FinancialIntelligenceServer()
    await server.run()


def main():
    """Main entry point that handles asyncio properly."""
    try:
        # Check if we're already in an event loop (Claude Desktop scenario)
        loop = asyncio.get_running_loop()
        # If we reach here, there's already a loop running
        # Create a task in the existing loop
        task = loop.create_task(run_server())
        return task
    except RuntimeError:
        # No existing loop, safe to use asyncio.run()
        try:
            asyncio.run(run_server())
        except RuntimeError as e:
            if "already running" in str(e):
                # Handle the specific asyncio conflict
                print("Asyncio loop conflict detected", file=sys.stderr)
                sys.exit(1)
            else:
                raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)
