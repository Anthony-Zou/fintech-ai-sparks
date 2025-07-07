"""
Main Entry Point for MCP Financial Intelligence Server (Clean Version)

This module provides the main entry point for running the MCP Financial Intelligence Server.
Completely clean version without any asyncio conflicts or stdout interference.
"""

from mcp_server.server_fixed import FinancialIntelligenceServer
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the fixed server

# Configure logging to stderr only (not stdout)
logging.basicConfig(
    level=logging.WARNING,  # Reduced logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Log to stderr, not stdout
    ]
)


def main() -> None:
    """Main entry point for the MCP Financial Intelligence Server."""
    try:
        # Create and run server without asyncio.run() to avoid conflicts
        server = FinancialIntelligenceServer()

        # Use the server's run method directly
        import asyncio
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, server.run())
                    future.result()
            else:
                # If no loop is running, use asyncio.run
                asyncio.run(server.run())
        except RuntimeError:
            # If no event loop, create new one
            asyncio.run(server.run())

    except KeyboardInterrupt:
        logging.info("MCP Financial Intelligence Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error starting MCP Financial Intelligence Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
