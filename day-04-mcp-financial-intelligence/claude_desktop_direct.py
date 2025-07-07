#!/usr/bin/env python3
"""
MCP Financial Intelligence Server for Claude Desktop

Direct MCP protocol implementation avoiding FastMCP's run() method that causes asyncio conflicts.
"""

from mcp_server.server import FinancialIntelligenceServer
import sys
import asyncio
import json
import logging
from typing import Any, Dict, List

# Configure minimal logging to stderr only
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Import our working server functionality


class ClaudeDesktopMCPServer:
    """MCP server specifically designed for Claude Desktop stdio communication."""

    def __init__(self):
        """Initialize the server with direct access to financial intelligence functionality."""
        # Create the financial server instance (this works from integration tests)
        self.financial_server = FinancialIntelligenceServer()

    async def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests and route to appropriate handlers."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "financial-intelligence",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "tools/list":
                tools = [
                    {
                        "name": "analyze_market_trends",
                        "description": "Analyze market trends and generate forecasts using Day 1 platform",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "symbols": {"type": "array", "items": {"type": "string"}},
                                "timeframe": {"type": "string", "default": "1y"},
                                "forecast_days": {"type": "integer", "default": 30},
                                "analysis_type": {"type": "array", "items": {"type": "string"}, "default": ["volume", "price"]}
                            },
                            "required": ["symbols"]
                        }
                    },
                    {
                        "name": "optimize_portfolio",
                        "description": "Optimize portfolio allocation using Day 2 risk analytics platform",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "symbols": {"type": "array", "items": {"type": "string"}},
                                "optimization_method": {"type": "string", "default": "max_sharpe"},
                                "risk_free_rate": {"type": "number", "default": 0.02}
                            },
                            "required": ["symbols"]
                        }
                    },
                    {
                        "name": "calculate_risk_metrics",
                        "description": "Calculate comprehensive risk metrics using Day 2 platform",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "symbols": {"type": "array", "items": {"type": "string"}},
                                "weights": {"type": "array", "items": {"type": "number"}},
                                "confidence_levels": {"type": "array", "items": {"type": "number"}, "default": [0.95, 0.99]},
                                "portfolio_value": {"type": "number", "default": 100000}
                            },
                            "required": ["symbols", "weights"]
                        }
                    },
                    {
                        "name": "generate_financial_insights",
                        "description": "Generate unified financial insights combining all platforms",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "symbols": {"type": "array", "items": {"type": "string"}},
                                "analysis_scope": {"type": "string", "default": "comprehensive"}
                            },
                            "required": ["symbols"]
                        }
                    }
                ]

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                # Route to appropriate handler using the working pattern from integration tests
                if tool_name == "analyze_market_trends":
                    result = await self.financial_server._handle_market_analysis(arguments)
                elif tool_name == "optimize_portfolio":
                    result = await self.financial_server._handle_portfolio_optimization(arguments)
                elif tool_name == "calculate_risk_metrics":
                    result = await self.financial_server._handle_risk_metrics(arguments)
                elif tool_name == "generate_financial_insights":
                    result = await self.financial_server._handle_financial_insights(arguments)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def run_stdio(self):
        """Run MCP server with stdio communication for Claude Desktop."""
        while True:
            try:
                # Read line from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                # Parse JSON request
                request = json.loads(line.strip())

                # Handle request
                response = await self.handle_mcp_request(request)

                # Send JSON response to stdout
                print(json.dumps(response))
                sys.stdout.flush()

            except EOFError:
                break
            except Exception as e:
                # Send error response
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Server error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


async def main():
    """Main entry point."""
    server = ClaudeDesktopMCPServer()
    await server.run_stdio()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)
