"""
MCP Financial Intelligence Client

Client for connecting to and interacting with the MCP Financial Intelligence Server.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp.types import Tool, CallToolRequest, CallToolResult


class MCPFinancialClient:
    """
    Client for the MCP Financial Intelligence Server.

    Provides high-level methods for interacting with the unified financial platform.
    """

    def __init__(self, server_command: str = "python -m mcp_server.main"):
        self.server_command = server_command
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Tool] = []
        self.logger = logging.getLogger(__name__)
        self._stdio_context = None

    async def connect(self) -> bool:
        """
        Connect to the MCP Financial Intelligence Server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create client session using stdio context manager
            self._stdio_context = stdio_client(self.server_command.split())
            read_stream, write_stream = await self._stdio_context.__aenter__()

            self.session = ClientSession(read_stream, write_stream)

            # Initialize the session
            await self.session.initialize()

            # Get available tools
            tools_response = await self.session.list_tools()
            self.available_tools = tools_response.tools

            self.logger.info(
                f"Connected to MCP Financial Intelligence Server with {len(self.available_tools)} tools")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            self.session = None

        if self._stdio_context:
            await self._stdio_context.__aexit__(None, None, None)
            self._stdio_context = None

    async def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.available_tools]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response data
        """
        if not self.session:
            raise ConnectionError("Not connected to MCP server")

        try:
            # Call the tool
            result = await self.session.call_tool(
                CallToolRequest(
                    name=tool_name,
                    arguments=arguments
                )
            )

            # Parse the response
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    # Try to parse as JSON, fallback to text
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"text": content.text}
                else:
                    return {"content": str(content)}
            else:
                return {"error": "No content in response"}

        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}

    # High-level methods for financial intelligence operations

    async def analyze_market_trends(self, symbols: List[str], timeframe: str = "1y",
                                    forecast_days: int = 30,
                                    analysis_type: List[str] = None) -> Dict[str, Any]:
        """
        Analyze market trends using Day 1 platform integration.

        Args:
            symbols: Stock symbols to analyze
            timeframe: Data timeframe
            forecast_days: Days to forecast
            analysis_type: Types of analysis

        Returns:
            Market analysis results
        """
        if analysis_type is None:
            analysis_type = ["volume", "price"]

        arguments = {
            "symbols": symbols,
            "timeframe": timeframe,
            "forecast_days": forecast_days,
            "analysis_type": analysis_type
        }

        return await self.call_tool("analyze_market_trends", arguments)

    async def optimize_portfolio(self, symbols: List[str], method: str = "max_sharpe",
                                 risk_free_rate: float = 0.02, constraints: Dict = None,
                                 views: Dict = None) -> Dict[str, Any]:
        """
        Optimize portfolio using Day 2 platform integration.

        Args:
            symbols: Portfolio assets
            method: Optimization method
            risk_free_rate: Risk-free rate
            constraints: Weight constraints
            views: Expected returns views

        Returns:
            Portfolio optimization results
        """
        arguments = {
            "symbols": symbols,
            "optimization_method": method,
            "risk_free_rate": risk_free_rate
        }

        if constraints:
            arguments["constraints"] = constraints
        if views:
            arguments["views"] = views

        return await self.call_tool("optimize_portfolio", arguments)

    async def calculate_risk_metrics(self, symbols: List[str], weights: List[float],
                                     confidence_levels: List[float] = None,
                                     portfolio_value: float = 100000) -> Dict[str, Any]:
        """
        Calculate comprehensive risk metrics using Day 2 platform.

        Args:
            symbols: Portfolio assets
            weights: Portfolio weights
            confidence_levels: VaR confidence levels
            portfolio_value: Portfolio value

        Returns:
            Risk metrics results
        """
        if confidence_levels is None:
            confidence_levels = [0.95, 0.99]

        arguments = {
            "symbols": symbols,
            "weights": weights,
            "confidence_levels": confidence_levels,
            "portfolio_value": portfolio_value
        }

        return await self.call_tool("calculate_risk_metrics", arguments)

    async def monte_carlo_simulation(self, symbols: List[str], weights: List[float],
                                     num_simulations: int = 10000, time_horizon: int = 252,
                                     scenarios: List[str] = None) -> Dict[str, Any]:
        """
        Run Monte Carlo stress testing using Day 2 platform.

        Args:
            symbols: Portfolio assets
            weights: Portfolio weights
            num_simulations: Number of simulations
            time_horizon: Time horizon in days
            scenarios: Market scenarios

        Returns:
            Monte Carlo simulation results
        """
        if scenarios is None:
            scenarios = ["bull_market", "bear_market", "market_crash"]

        arguments = {
            "symbols": symbols,
            "weights": weights,
            "num_simulations": num_simulations,
            "time_horizon": time_horizon,
            "scenarios": scenarios
        }

        return await self.call_tool("monte_carlo_simulation", arguments)

    async def execute_trading_strategy(self, strategy_type: str, symbols: List[str],
                                       parameters: Dict = None) -> Dict[str, Any]:
        """
        Execute trading strategy using Day 3 platform.

        Args:
            strategy_type: Strategy type
            symbols: Symbols to trade
            parameters: Strategy parameters

        Returns:
            Strategy execution results
        """
        arguments = {
            "strategy_type": strategy_type,
            "symbols": symbols
        }

        if parameters:
            arguments["parameters"] = parameters

        return await self.call_tool("execute_trading_strategy", arguments)

    async def manage_positions(self, action: str, symbol: str = None,
                               quantity: float = None) -> Dict[str, Any]:
        """
        Manage trading positions using Day 3 platform.

        Args:
            action: Position action
            symbol: Symbol (optional)
            quantity: Quantity (optional)

        Returns:
            Position management results
        """
        arguments = {"action": action}

        if symbol:
            arguments["symbol"] = symbol
        if quantity:
            arguments["quantity"] = quantity

        return await self.call_tool("manage_positions", arguments)

    async def generate_financial_insights(self, symbols: List[str],
                                          analysis_scope: str = "comprehensive",
                                          context: Dict = None) -> Dict[str, Any]:
        """
        Generate unified financial insights combining all platforms.

        Args:
            symbols: Symbols to analyze
            analysis_scope: Scope of analysis
            context: Analysis context

        Returns:
            Unified financial insights
        """
        arguments = {
            "symbols": symbols,
            "analysis_scope": analysis_scope
        }

        if context:
            arguments["context"] = context

        return await self.call_tool("generate_financial_insights", arguments)

    async def portfolio_rebalancing_advice(self, current_portfolio: Dict[str, float],
                                           target_allocation: Dict[str,
                                                                   float] = None,
                                           rebalancing_frequency: str = "quarterly",
                                           transaction_cost: float = 0.001) -> Dict[str, Any]:
        """
        Generate portfolio rebalancing recommendations.

        Args:
            current_portfolio: Current portfolio holdings
            target_allocation: Target allocation
            rebalancing_frequency: Rebalancing frequency
            transaction_cost: Transaction cost

        Returns:
            Rebalancing advice
        """
        arguments = {
            "current_portfolio": current_portfolio,
            "rebalancing_frequency": rebalancing_frequency,
            "transaction_cost": transaction_cost
        }

        if target_allocation:
            arguments["target_allocation"] = target_allocation

        return await self.call_tool("portfolio_rebalancing_advice", arguments)

    # Utility methods

    async def health_check(self) -> Dict[str, Any]:
        """Check if the MCP server is healthy."""
        try:
            tools = await self.get_available_tools()
            return {
                "status": "healthy",
                "available_tools": len(tools),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server."""
        if not self.session:
            return {"error": "Not connected to server"}

        return {
            "connected": True,
            "available_tools": [tool.name for tool in self.available_tools],
            "tool_count": len(self.available_tools),
            "server_command": self.server_command
        }


# Context manager for easy client usage
class MCPFinancialClientManager:
    """Context manager for MCP Financial Client."""

    def __init__(self, server_command: str = "python -m mcp_server.main"):
        self.client = MCPFinancialClient(server_command)

    async def __aenter__(self) -> MCPFinancialClient:
        """Async context manager entry."""
        await self.client.connect()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.client.disconnect()


# Convenience function for one-off operations
async def with_mcp_client(operation, *args, **kwargs):
    """
    Execute an operation with MCP client in a context manager.

    Args:
        operation: Async function to execute with client as first argument
        *args: Additional arguments for operation
        **kwargs: Additional keyword arguments for operation

    Returns:
        Result of the operation
    """
    async with MCPFinancialClientManager() as client:
        return await operation(client, *args, **kwargs)
