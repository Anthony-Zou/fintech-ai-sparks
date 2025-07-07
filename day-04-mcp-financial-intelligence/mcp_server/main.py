"""
Main Entry Point for MCP Financial Intelligence Server

This module provides the main entry point for running the MCP Financial Intelligence Server.
"""

from mcp_server.server import main as server_main
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main() -> None:
    """Main entry point for the MCP Financial Intelligence Server."""
    try:
        print("🚀 Starting MCP Financial Intelligence Server...")
        print("📊 Integrating Day 1-3 platforms with MCP orchestration layer")
        print("🔧 Initializing unified financial intelligence capabilities...")

        # Run the server
        asyncio.run(server_main())

    except KeyboardInterrupt:
        print("\n👋 MCP Financial Intelligence Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting MCP Financial Intelligence Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
