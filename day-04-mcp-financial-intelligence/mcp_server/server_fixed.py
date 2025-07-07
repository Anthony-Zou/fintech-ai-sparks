"""
MCP Financial Intelligence Server (Fixed for Claude Desktop)

Unified AI-powered financial intelligence platform that integrates:
- Day 1: Market Analysis & Forecasting
- Day 2: Portfolio Risk Management  
- Day 3: Algorithmic Trading
- Day 4: MCP Orchestration Layer

Fixed version with proper logging configuration to avoid JSON protocol interference.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import FastMCP
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Configure logging to stderr only (not stdout) to avoid MCP JSON protocol interference
logging.basicConfig(
    level=logging.WARNING,  # Reduced logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Log to stderr, not stdout
    ]
)
logger = logging.getLogger(__name__)


class FinancialIntelligenceServer:
    """Main MCP server for unified financial intelligence platform."""

    def __init__(self):
        self.mcp = FastMCP("financial-intelligence")
        self.connectors = {}
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Setup all MCP tools for financial intelligence."""

        @self.mcp.tool()
        async def analyze_market_trends(
            symbols: List[str],
            timeframe: str = "1y",
            forecast_days: int = 30,
            analysis_type: List[str] = ["volume", "price"]
        ) -> str:
            """Analyze market trends and generate forecasts using Day 1 platform."""
            return await self._handle_market_analysis({
                "symbols": symbols,
                "timeframe": timeframe,
                "forecast_days": forecast_days,
                "analysis_type": analysis_type
            })

        @self.mcp.tool()
        async def optimize_portfolio(
            symbols: List[str],
            optimization_method: str = "max_sharpe",
            risk_free_rate: float = 0.02,
            constraints: Optional[Dict[str, Any]] = None,
            views: Optional[Dict[str, Any]] = None
        ) -> str:
            """Optimize portfolio allocation using Day 2 risk analytics platform."""
            return await self._handle_portfolio_optimization({
                "symbols": symbols,
                "optimization_method": optimization_method,
                "risk_free_rate": risk_free_rate,
                "constraints": constraints or {},
                "views": views or {}
            })

        @self.mcp.tool()
        async def calculate_risk_metrics(
            symbols: List[str],
            weights: List[float],
            confidence_levels: List[float] = [0.95, 0.99],
            portfolio_value: float = 100000
        ) -> str:
            """Calculate comprehensive risk metrics using Day 2 platform."""
            return await self._handle_risk_metrics({
                "symbols": symbols,
                "weights": weights,
                "confidence_levels": confidence_levels,
                "portfolio_value": portfolio_value
            })

        @self.mcp.tool()
        async def monte_carlo_simulation(
            symbols: List[str],
            weights: List[float],
            num_simulations: int = 10000,
            time_horizon: int = 252,
            scenarios: List[str] = ["bull_market",
                                    "bear_market", "market_crash"]
        ) -> str:
            """Run Monte Carlo stress testing using Day 2 platform."""
            return await self._handle_monte_carlo({
                "symbols": symbols,
                "weights": weights,
                "num_simulations": num_simulations,
                "time_horizon": time_horizon,
                "scenarios": scenarios
            })

        @self.mcp.tool()
        async def execute_trading_strategy(
            strategy_type: str,
            symbols: List[str],
            parameters: Dict[str, Any],
            execution_mode: str = "simulation"
        ) -> str:
            """Execute algorithmic trading strategies using Day 3 platform."""
            return await self._handle_trading_strategy({
                "strategy_type": strategy_type,
                "symbols": symbols,
                "parameters": parameters,
                "execution_mode": execution_mode
            })

        @self.mcp.tool()
        async def manage_positions(
            action: str,
            symbol: Optional[str] = None,
            quantity: Optional[int] = None
        ) -> str:
            """Manage trading positions using Day 3 platform."""
            return await self._handle_position_management({
                "action": action,
                "symbol": symbol,
                "quantity": quantity
            })

        @self.mcp.tool()
        async def generate_financial_insights(
            symbols: List[str],
            analysis_scope: str = "comprehensive",
            context: Optional[Dict[str, Any]] = None
        ) -> str:
            """Generate unified financial insights combining all platforms."""
            return await self._handle_financial_insights({
                "symbols": symbols,
                "analysis_scope": analysis_scope,
                "context": context or {}
            })

        @self.mcp.tool()
        async def portfolio_rebalancing_advice(
            current_portfolio: Dict[str, float],
            target_allocation: Dict[str, float],
            rebalancing_frequency: str = "quarterly",
            transaction_cost: float = 0.001
        ) -> str:
            """Generate portfolio rebalancing recommendations."""
            return await self._handle_rebalancing_advice({
                "current_portfolio": current_portfolio,
                "target_allocation": target_allocation,
                "rebalancing_frequency": rebalancing_frequency,
                "transaction_cost": transaction_cost
            })

    async def _handle_market_analysis(self, arguments: Dict[str, Any]) -> str:
        """Handle market analysis using Day 1 platform integration."""
        # This would integrate with the Day 1 demand forecasting platform
        symbols = arguments.get("symbols", [])
        timeframe = arguments.get("timeframe", "1y")
        forecast_days = arguments.get("forecast_days", 30)
        analysis_type = arguments.get("analysis_type", ["volume", "price"])

        # Mock implementation - in real scenario, this would call Day 1 platform
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "symbols_analyzed": symbols,
            "timeframe": timeframe,
            "forecast_horizon": forecast_days,
            "market_analysis": {},
            "forecasts": {},
            "technical_indicators": {},
            "recommendations": []
        }

        for symbol in symbols:
            # Simulate market analysis results
            results["market_analysis"][symbol] = {
                "current_price": 150.0 + np.random.normal(0, 5),
                "price_change_24h": np.random.normal(0, 2),
                "volume_trend": "increasing" if np.random.random() > 0.5 else "decreasing",
                "volatility_30d": np.random.uniform(15, 40),
                "momentum_score": np.random.uniform(-1, 1)
            }

            if "price" in analysis_type:
                results["forecasts"][symbol] = {
                    "price_forecast": {
                        f"day_{i}": 150.0 + np.random.normal(0, 2) for i in range(1, forecast_days + 1)
                    },
                    "confidence_intervals": {
                        "upper_95": [155.0 + i * 0.1 for i in range(forecast_days)],
                        "lower_95": [145.0 - i * 0.1 for i in range(forecast_days)]
                    }
                }

            if "volume" in analysis_type:
                results["forecasts"][symbol]["volume_forecast"] = {
                    f"day_{i}": 1000000 + np.random.normal(0, 100000) for i in range(1, forecast_days + 1)
                }

            # Generate recommendations
            momentum = results["market_analysis"][symbol]["momentum_score"]
            if momentum > 0.3:
                recommendation = "BUY - Strong positive momentum detected"
            elif momentum < -0.3:
                recommendation = "SELL - Negative momentum detected"
            else:
                recommendation = "HOLD - Neutral momentum"

            results["recommendations"].append({
                "symbol": symbol,
                "action": recommendation,
                "confidence": abs(momentum),
                "reasoning": f"Based on momentum score of {momentum:.3f}"
            })

        return json.dumps(results, indent=2)

    async def _handle_portfolio_optimization(self, arguments: Dict[str, Any]) -> str:
        """Handle portfolio optimization using Day 2 platform integration."""
        symbols = arguments.get("symbols", [])
        method = arguments.get("optimization_method", "max_sharpe")
        risk_free_rate = arguments.get("risk_free_rate", 0.02)
        constraints = arguments.get("constraints", {})
        views = arguments.get("views", {})

        # Mock optimization results
        n_assets = len(symbols)
        # Random weights that sum to 1
        weights = np.random.dirichlet(np.ones(n_assets))

        results = {
            "optimization_timestamp": datetime.now().isoformat(),
            "method": method,
            "symbols": symbols,
            "optimal_weights": {symbol: float(weight) for symbol, weight in zip(symbols, weights)},
            "portfolio_metrics": {
                "expected_return": 0.08 + np.random.normal(0, 0.02),
                "volatility": 0.15 + np.random.normal(0, 0.03),
                "sharpe_ratio": 0.53 + np.random.normal(0, 0.1),
                "max_drawdown": -0.12 + np.random.normal(0, 0.02)
            },
            "risk_free_rate": risk_free_rate,
            "constraints_applied": constraints,
            "optimization_status": "success"
        }

        if method == "black_litterman" and views:
            results["views_incorporated"] = views

        return json.dumps(results, indent=2)

    async def _handle_risk_metrics(self, arguments: Dict[str, Any]) -> str:
        """Handle risk metrics calculation using Day 2 platform integration."""
        symbols = arguments.get("symbols", [])
        weights = arguments.get("weights", [])
        confidence_levels = arguments.get("confidence_levels", [0.95, 0.99])
        portfolio_value = arguments.get("portfolio_value", 100000)

        # Mock risk metrics calculation
        results = {
            "calculation_timestamp": datetime.now().isoformat(),
            "portfolio_composition": {symbol: weight for symbol, weight in zip(symbols, weights)},
            "portfolio_value": portfolio_value,
            "risk_metrics": {
                "value_at_risk": {},
                "expected_shortfall": {},
                "volatility_metrics": {
                    "daily_volatility": 0.015 + np.random.normal(0, 0.003),
                    "annual_volatility": 0.23 + np.random.normal(0, 0.05),
                    "downside_deviation": 0.18 + np.random.normal(0, 0.03)
                },
                "performance_ratios": {
                    "sharpe_ratio": 0.65 + np.random.normal(0, 0.15),
                    "sortino_ratio": 0.85 + np.random.normal(0, 0.20),
                    "calmar_ratio": 0.45 + np.random.normal(0, 0.10)
                },
                "drawdown_analysis": {
                    "max_drawdown_percent": -15.5 + np.random.normal(0, 3),
                    "average_drawdown": -8.2 + np.random.normal(0, 2),
                    "recovery_time_days": 65 + np.random.randint(-20, 30)
                }
            }
        }

        # Calculate VaR for different confidence levels
        for conf_level in confidence_levels:
            var_daily = portfolio_value * 0.025 * \
                (1 + (1-conf_level) * 2)  # Mock calculation
            results["risk_metrics"]["value_at_risk"][f"VaR_{int(conf_level*100)}"] = {
                "daily": -var_daily,
                "weekly": -var_daily * np.sqrt(7),
                "monthly": -var_daily * np.sqrt(30),
                "annual": -var_daily * np.sqrt(252)
            }

            # Expected Shortfall (CVaR)
            es_daily = var_daily * 1.3  # ES is typically higher than VaR
            results["risk_metrics"]["expected_shortfall"][f"ES_{int(conf_level*100)}"] = {
                "daily": -es_daily,
                "weekly": -es_daily * np.sqrt(7),
                "monthly": -es_daily * np.sqrt(30),
                "annual": -es_daily * np.sqrt(252)
            }

        return json.dumps(results, indent=2)

    async def _handle_monte_carlo(self, arguments: Dict[str, Any]) -> str:
        """Handle Monte Carlo simulation using Day 2 platform integration."""
        symbols = arguments.get("symbols", [])
        weights = arguments.get("weights", [])
        num_simulations = arguments.get("num_simulations", 10000)
        time_horizon = arguments.get("time_horizon", 252)
        scenarios = arguments.get(
            "scenarios", ["bull_market", "bear_market", "market_crash"])

        # Mock Monte Carlo simulation results
        results = {
            "simulation_timestamp": datetime.now().isoformat(),
            "parameters": {
                "num_simulations": num_simulations,
                "time_horizon_days": time_horizon,
                "portfolio_composition": {symbol: weight for symbol, weight in zip(symbols, weights)}
            },
            "simulation_results": {
                "final_values": {
                    "mean": 105000 + np.random.normal(0, 5000),
                    "median": 103000 + np.random.normal(0, 3000),
                    "std": 18000 + np.random.normal(0, 2000),
                    "min": 65000 + np.random.normal(0, 5000),
                    "max": 160000 + np.random.normal(0, 10000)
                },
                "return_distribution": {
                    "mean_return": 0.05 + np.random.normal(0, 0.02),
                    "volatility": 0.18 + np.random.normal(0, 0.03),
                    "skewness": -0.2 + np.random.normal(0, 0.1),
                    "kurtosis": 3.5 + np.random.normal(0, 0.5)
                },
                "percentiles": {
                    "5th": 78000 + np.random.normal(0, 3000),
                    "25th": 92000 + np.random.normal(0, 2000),
                    "50th": 103000 + np.random.normal(0, 3000),
                    "75th": 118000 + np.random.normal(0, 3000),
                    "95th": 142000 + np.random.normal(0, 5000)
                }
            },
            "scenario_analysis": {}
        }

        # Generate scenario-specific results
        for scenario in scenarios:
            if scenario == "bull_market":
                mean_return = 0.12
                volatility = 0.14
            elif scenario == "bear_market":
                mean_return = -0.08
                volatility = 0.22
            elif scenario == "market_crash":
                mean_return = -0.25
                volatility = 0.35
            else:
                mean_return = 0.05
                volatility = 0.18

            results["scenario_analysis"][scenario] = {
                "expected_return": mean_return,
                "volatility": volatility,
                "probability_of_loss": 1 - (mean_return + 1),
                "worst_case_loss": mean_return - 2 * volatility,
                "scenario_description": f"Scenario modeling {scenario.replace('_', ' ')}"
            }

        return json.dumps(results, indent=2)

    async def _handle_trading_strategy(self, arguments: Dict[str, Any]) -> str:
        """Handle trading strategy execution using Day 3 platform integration."""
        strategy_type = arguments.get("strategy_type")
        symbols = arguments.get("symbols", [])
        parameters = arguments.get("parameters", {})
        execution_mode = arguments.get("execution_mode", "simulation")

        # Mock trading strategy results
        results = {
            "execution_timestamp": datetime.now().isoformat(),
            "strategy_type": strategy_type,
            "execution_mode": execution_mode,
            "symbols": symbols,
            "parameters": parameters,
            "strategy_status": "active",
            "performance_summary": {
                "total_trades": np.random.randint(50, 200),
                "winning_trades": np.random.randint(25, 120),
                "total_pnl": np.random.normal(5000, 2000),
                "win_rate": np.random.uniform(0.45, 0.65),
                "sharpe_ratio": np.random.uniform(0.8, 1.4),
                "max_drawdown": np.random.uniform(-0.15, -0.05)
            },
            "current_positions": {},
            "recent_trades": []
        }

        # Generate mock positions and trades
        for symbol in symbols:
            # Mock strategy signals
            signal_strength = np.random.uniform(-1, 1)
            if strategy_type == "momentum":
                if signal_strength > 0.3:
                    signal = "BUY"
                elif signal_strength < -0.3:
                    signal = "SELL"
                else:
                    signal = "HOLD"
            else:
                signal = np.random.choice(["BUY", "SELL", "HOLD"])

            results["current_positions"][symbol] = {
                "signal": signal,
                "signal_strength": signal_strength,
                "position_size": np.random.randint(-100, 100),
                "entry_price": 150.0 + np.random.normal(0, 10),
                "current_price": 152.0 + np.random.normal(0, 5),
                "unrealized_pnl": np.random.normal(0, 500)
            }

            # Mock current positions
            position_size = np.random.randint(-200, 200)
            if position_size != 0:
                results["current_positions"][symbol] = {
                    "quantity": position_size,
                    "avg_price": 150.0 + np.random.normal(0, 10),
                    "current_price": 152.0 + np.random.normal(0, 5),
                    "unrealized_pnl": position_size * np.random.normal(0, 2)
                }

        # Mock recent trades
        for i in range(5):
            symbol = np.random.choice(symbols)
            results["recent_trades"].append({
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "symbol": symbol,
                "side": np.random.choice(["BUY", "SELL"]),
                "quantity": np.random.randint(50, 200),
                "price": 150.0 + np.random.normal(0, 5),
                "pnl": np.random.normal(0, 100)
            })

        return json.dumps(results, indent=2)

    async def _handle_position_management(self, arguments: Dict[str, Any]) -> str:
        """Handle position management using Day 3 platform integration."""
        action = arguments.get("action")
        symbol = arguments.get("symbol")
        quantity = arguments.get("quantity")

        results = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "symbol": symbol,
            "status": "success"
        }

        if action == "get_positions":
            # Mock current positions
            results["positions"] = {
                "AAPL": {"quantity": 100, "avg_price": 150.0, "current_price": 152.0, "unrealized_pnl": 200},
                "MSFT": {"quantity": -50, "avg_price": 300.0, "current_price": 295.0, "unrealized_pnl": 250},
                "TSLA": {"quantity": 75, "avg_price": 200.0, "current_price": 195.0, "unrealized_pnl": -375}
            }
            results["total_pnl"] = sum(pos["unrealized_pnl"]
                                       for pos in results["positions"].values())

        elif action == "close_position" and symbol:
            results["closed_position"] = {
                "symbol": symbol,
                "quantity_closed": 100,
                "closing_price": 151.5,
                "realized_pnl": 150.0
            }

        elif action == "update_position" and symbol and quantity:
            results["updated_position"] = {
                "symbol": symbol,
                "new_quantity": quantity,
                "execution_price": 151.0 + np.random.normal(0, 2),
                "timestamp": datetime.now().isoformat()
            }

        return json.dumps(results, indent=2)

    async def _handle_financial_insights(self, arguments: Dict[str, Any]) -> str:
        """Generate unified financial insights combining all platforms."""
        symbols = arguments.get("symbols", [])
        analysis_scope = arguments.get("analysis_scope", "comprehensive")
        context = arguments.get("context", {})

        # This would integrate data from all Day 1-3 platforms
        insights = {
            "analysis_timestamp": datetime.now().isoformat(),
            "symbols_analyzed": symbols,
            "analysis_scope": analysis_scope,
            "context": context,
            "unified_insights": {
                "market_outlook": "NEUTRAL_TO_BULLISH",
                "key_insights": [
                    "Strong momentum detected in tech sector with positive volume forecasts",
                    "Portfolio optimization suggests reducing concentration risk",
                    "Current market volatility presents tactical trading opportunities",
                    "Risk metrics indicate portfolio within acceptable parameters"
                ],
                "risk_assessment": {
                    "overall_risk_level": "MODERATE",
                    "primary_risks": ["Market volatility", "Concentration risk", "Sector correlation"],
                    "risk_mitigation": ["Diversification", "Position sizing", "Stop-loss implementation"]
                },
                "opportunities": [
                    "Momentum signals suggest potential upside in growth stocks",
                    "Mean reversion opportunities in oversold value names",
                    "Volatility trading strategies may be profitable"
                ],
                "recommendations": {
                    "immediate_actions": [
                        "Rebalance portfolio to reduce concentration risk",
                        "Implement momentum trading strategy for selected symbols",
                        "Monitor VaR limits closely given increased volatility"
                    ],
                    "medium_term_actions": [
                        "Consider increasing defensive allocation",
                        "Evaluate alternative asset exposure",
                        "Review and update risk parameters"
                    ]
                }
            },
            "cross_platform_correlation": {
                "forecast_trading_alignment": "HIGH",
                "risk_strategy_consistency": "MODERATE",
                "optimization_execution_sync": "HIGH"
            }
        }

        # Add symbol-specific insights
        symbol_insights = {}
        for symbol in symbols:
            symbol_insights[symbol] = {
                "technical_outlook": np.random.choice(["BULLISH", "BEARISH", "NEUTRAL"]),
                "risk_contribution": np.random.uniform(0.1, 0.3),
                "trading_signal": np.random.choice(["BUY", "SELL", "HOLD"]),
                "forecast_confidence": np.random.uniform(0.6, 0.9),
                "recommended_weight": np.random.uniform(0.05, 0.25)
            }

        insights["symbol_specific_insights"] = symbol_insights

        return json.dumps(insights, indent=2)

    async def _handle_rebalancing_advice(self, arguments: Dict[str, Any]) -> str:
        """Generate portfolio rebalancing recommendations."""
        current_portfolio = arguments.get("current_portfolio", {})
        target_allocation = arguments.get("target_allocation", {})
        rebalancing_frequency = arguments.get(
            "rebalancing_frequency", "quarterly")
        transaction_cost = arguments.get("transaction_cost", 0.001)

        # Mock rebalancing analysis
        advice = {
            "analysis_timestamp": datetime.now().isoformat(),
            "current_portfolio": current_portfolio,
            "rebalancing_frequency": rebalancing_frequency,
            "transaction_cost_percent": transaction_cost * 100,
            "rebalancing_analysis": {
                "rebalancing_needed": True,
                "total_drift": 0.15,  # 15% total drift from target
                "rebalancing_cost": 850.00,
                "expected_benefit": 1200.00,
                "net_benefit": 350.00,
                "recommendation": "PROCEED"
            },
            "detailed_adjustments": {},
            "implementation_plan": {
                "execution_order": [],
                "timing_recommendation": "Execute during high liquidity hours",
                "risk_considerations": ["Market impact", "Timing risk", "Execution costs"]
            },
            "alternative_strategies": [
                "Gradual rebalancing over 2 weeks",
                "Threshold-based rebalancing (10% drift trigger)",
                "Cash flow-based rebalancing"
            ]
        }

        # Calculate specific adjustments needed
        for symbol, current_weight in current_portfolio.items():
            target_weight = target_allocation.get(symbol, current_weight)
            weight_diff = target_weight - current_weight

            if abs(weight_diff) > 0.05:  # 5% threshold
                advice["detailed_adjustments"][symbol] = {
                    "current_weight": current_weight,
                    "target_weight": target_weight,
                    "adjustment_needed": weight_diff,
                    "action": "BUY" if weight_diff > 0 else "SELL",
                    "urgency": "HIGH" if abs(weight_diff) > 0.15 else "MEDIUM"
                }

                advice["implementation_plan"]["execution_order"].append({
                    "symbol": symbol,
                    "action": "BUY" if weight_diff > 0 else "SELL",
                    "priority": 1 if abs(weight_diff) > 0.15 else 2
                })

        return json.dumps(advice, indent=2)

    async def run(self) -> None:
        """Run the MCP server."""
        await self.mcp.run()


# Main execution
async def main() -> None:
    """Main entry point for the MCP Financial Intelligence Server."""
    server = FinancialIntelligenceServer()
    await server.run()
