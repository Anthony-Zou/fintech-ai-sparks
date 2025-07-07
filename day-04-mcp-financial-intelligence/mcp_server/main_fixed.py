"""
Main Entry Point for MCP Financial Intelligence Server

This module provides the main entry point for running the MCP Financial Intelligence Server.
Clean version without stdout output that interferes with MCP JSON protocol.
"""

from mcp_server.server import main as server_main
import asyncio
import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
        # No print statements to stdout - MCP protocol requires clean JSON only
        asyncio.run(server_main())
    except KeyboardInterrupt:
        # Log to stderr, not stdout
        logging.info("MCP Financial Intelligence Server stopped by user")
        sys.exit(0)
    except Exception as e:
        # Log to stderr, not stdout
        logging.error(f"Error starting MCP Financial Intelligence Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
