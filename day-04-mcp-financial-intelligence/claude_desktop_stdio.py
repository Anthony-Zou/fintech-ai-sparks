#!/usr/bin/env python3
"""
MCP Server for Claude Desktop using stdio transport

Uses MCP library's stdio transport directly to avoid asyncio conflicts.
"""

from mcp_server.server import FinancialIntelligenceServer
import sys
import asyncio
import logging
import json
from typing import Any, Dict, List

# Configure minimal logging to stderr only
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Import our working server functionality


async def main():
    """Main entry point for stdio MCP server."""
    # Create our server instance
    financial_server = FinancialIntelligenceServer()

    # Use the MCP library's stdio server approach
    from mcp.server.stdio import stdio_server
    from mcp.server import Server
    from mcp.types import Tool, TextContent

    # Create MCP server
    server = Server("financial-intelligence")

    # Register our tools by wrapping the existing functionality
    @server.call_tool()
    async def analyze_market_trends(
        symbols: List[str],
        timeframe: str = "1y",
        forecast_days: int = 30,
        analysis_type: List[str] = ["volume", "price"]
    ) -> List[TextContent]:
        """Analyze market trends and generate forecasts."""
        result = await financial_server._handle_market_analysis({
            "symbols": symbols,
            "timeframe": timeframe,
            "forecast_days": forecast_days,
            "analysis_type": analysis_type
        })
        return [TextContent(type="text", text=result)]

    @server.call_tool()
    async def optimize_portfolio(
        symbols: List[str],
        optimization_method: str = "max_sharpe",
        risk_free_rate: float = 0.02
    ) -> List[TextContent]:
        """Optimize portfolio allocation."""
        result = await financial_server._handle_portfolio_optimization({
            "symbols": symbols,
            "optimization_method": optimization_method,
            "risk_free_rate": risk_free_rate,
            "constraints": {},
            "views": {}
        })
        return [TextContent(type="text", text=result)]

    @server.call_tool()
    async def calculate_risk_metrics(
        symbols: List[str],
        weights: List[float],
        confidence_levels: List[float] = [0.95, 0.99],
        portfolio_value: float = 100000
    ) -> List[TextContent]:
        """Calculate comprehensive risk metrics."""
        result = await financial_server._handle_risk_metrics({
            "symbols": symbols,
            "weights": weights,
            "confidence_levels": confidence_levels,
            "portfolio_value": portfolio_value
        })
        return [TextContent(type="text", text=result)]

    @server.call_tool()
    async def generate_financial_insights(
        symbols: List[str],
        analysis_scope: str = "comprehensive"
    ) -> List[TextContent]:
        """Generate unified financial insights."""
        result = await financial_server._handle_financial_insights({
            "symbols": symbols,
            "analysis_scope": analysis_scope,
            "context": {}
        })
        return [TextContent(type="text", text=result)]

    # Run the stdio server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)
