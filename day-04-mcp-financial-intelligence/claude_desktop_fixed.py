#!/usr/bin/env python3
"""
MCP Financial Intelligence Server for Claude Desktop

Properly conforming to MCP protocol specification for Claude Desktop.
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
                                "symbols": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of stock symbols to analyze"
                                },
                                "timeframe": {
                                    "type": "string",
                                    "description": "Time period for analysis (e.g., '1y', '6m', '3m')"
                                },
                                "forecast_days": {
                                    "type": "integer",
                                    "description": "Number of days to forecast ahead"
                                },
                                "analysis_type": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Types of analysis to perform"
                                }
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
                                "symbols": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of stock symbols for portfolio"
                                },
                                "optimization_method": {
                                    "type": "string",
                                    "description": "Optimization method (e.g., 'max_sharpe', 'min_volatility')"
                                },
                                "risk_free_rate": {
                                    "type": "number",
                                    "description": "Risk-free rate for optimization"
                                }
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
                                "symbols": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of stock symbols"
                                },
                                "weights": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "description": "Portfolio weights for each symbol"
                                },
                                "confidence_levels": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "description": "Confidence levels for VaR calculation"
                                },
                                "portfolio_value": {
                                    "type": "number",
                                    "description": "Total portfolio value"
                                }
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
                                "symbols": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of stock symbols to analyze"
                                },
                                "analysis_scope": {
                                    "type": "string",
                                    "description": "Scope of analysis (e.g., 'comprehensive', 'basic')"
                                }
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

                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: missing tool name"
                        }
                    }

                # Provide default values for optional parameters
                if tool_name == "analyze_market_trends":
                    arguments.setdefault("timeframe", "1y")
                    arguments.setdefault("forecast_days", 30)
                    arguments.setdefault("analysis_type", ["volume", "price"])
                    result = await self.financial_server._handle_market_analysis(arguments)
                elif tool_name == "optimize_portfolio":
                    arguments.setdefault("optimization_method", "max_sharpe")
                    arguments.setdefault("risk_free_rate", 0.02)
                    arguments.setdefault("constraints", {})
                    arguments.setdefault("views", {})
                    result = await self.financial_server._handle_portfolio_optimization(arguments)
                elif tool_name == "calculate_risk_metrics":
                    arguments.setdefault("confidence_levels", [0.95, 0.99])
                    arguments.setdefault("portfolio_value", 100000)
                    result = await self.financial_server._handle_risk_metrics(arguments)
                elif tool_name == "generate_financial_insights":
                    arguments.setdefault("analysis_scope", "comprehensive")
                    arguments.setdefault("context", {})
                    result = await self.financial_server._handle_financial_insights(arguments)
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }

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

                line = line.strip()
                if not line:
                    continue

                # Parse JSON request
                request = json.loads(line)

                # Handle request
                response = await self.handle_mcp_request(request)

                # Send JSON response to stdout
                print(json.dumps(response))
                sys.stdout.flush()

            except EOFError:
                break
            except json.JSONDecodeError as e:
                # Send JSON error response
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
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
