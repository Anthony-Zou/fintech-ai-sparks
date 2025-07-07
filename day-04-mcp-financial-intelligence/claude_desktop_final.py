#!/usr/bin/env python3
"""
MCP Financial Intelligence Server for Claude Desktop

Proper implementation that lets FastMCP handle stdio communication without asyncio conflicts.
"""

from mcp_server.server import FinancialIntelligenceServer
import sys
import logging

# Configure minimal logging to stderr only
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Import and create the server

# Create server instance - this registers all tools with FastMCP
server = FinancialIntelligenceServer()

# The FastMCP library will handle stdio communication automatically
# when Claude Desktop runs this script
# No asyncio.run() needed - that's what was causing the conflicts!
