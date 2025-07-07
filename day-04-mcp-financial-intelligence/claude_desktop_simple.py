#!/usr/bin/env python3
"""
Simple MCP Server for Claude Desktop

Avoids asyncio conflicts by letting MCP library handle event loop management.
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

# Create the server instance
server = FinancialIntelligenceServer()

# Let the MCP server handle its own event loop - don't call asyncio.run()
# This should work with Claude Desktop's stdio communication
