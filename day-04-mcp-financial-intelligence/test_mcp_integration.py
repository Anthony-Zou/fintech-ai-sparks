"""
MCP Financial Intelligence Platform Integration Tests

Comprehensive testing suite for validating MCP server functionality,
platform integrations, and cross-platform intelligence capabilities.
"""

import asyncio
import json
import time
from typing import Dict, List, Any
import pytest
from client.mcp_client import MCPFinancialClient


class MCPIntegrationTester:
    """Comprehensive MCP platform integration tester."""

    def __init__(self):
        self.client = MCPFinancialClient()
        self.test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        self.test_results = {}

    async def setup(self) -> bool:
        """Setup test environment."""
        print("🚀 Setting up MCP Integration Test Environment...")

        # Connect to MCP server
        connected = await self.client.connect()
        if not connected:
            print("❌ Failed to connect to MCP server")
            return False

        # Get available tools
        tools = await self.client.get_available_tools()
        print(f"✅ Connected to MCP server with {len(tools)} tools")
        print(f"📋 Available tools: {', '.join(tools)}")

        return True

    async def test_market_analysis_integration(self) -> Dict[str, Any]:
        """Test Day 1 platform integration - Market Analysis."""
        print("\n📊 Testing Market Analysis Integration (Day 1)...")

        test_results = {
            "test_name": "market_analysis",
            "platform": "Day 1",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test basic market analysis
            result = await self.client.analyze_market_trends(
                symbols=self.test_symbols[:2],  # Test with 2 symbols
                timeframe="6mo",
                forecast_days=30,
                analysis_type=["volume", "price"]
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Market analysis failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["response_size"] = len(str(result))
                test_results["has_forecasts"] = "forecasts" in result
                print("✅ Market analysis integration successful")
                print(
                    f"   📊 Response size: {test_results['response_size']} chars")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Market analysis test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_portfolio_optimization_integration(self) -> Dict[str, Any]:
        """Test Day 2 platform integration - Portfolio Optimization."""
        print("\n⚠️ Testing Portfolio Optimization Integration (Day 2)...")

        test_results = {
            "test_name": "portfolio_optimization",
            "platform": "Day 2",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test portfolio optimization
            result = await self.client.optimize_portfolio(
                symbols=self.test_symbols,
                method="max_sharpe",
                risk_free_rate=0.02
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Portfolio optimization failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["has_weights"] = "weights" in result
                test_results["has_metrics"] = "metrics" in result
                print("✅ Portfolio optimization integration successful")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Portfolio optimization test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_risk_metrics_integration(self) -> Dict[str, Any]:
        """Test risk metrics calculation."""
        print("\n📊 Testing Risk Metrics Integration...")

        test_results = {
            "test_name": "risk_metrics",
            "platform": "Day 2",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test with equal weights
            weights = [0.25, 0.25, 0.25, 0.25]

            result = await self.client.calculate_risk_metrics(
                symbols=self.test_symbols,
                weights=weights,
                confidence_levels=[0.95, 0.99],
                portfolio_value=100000
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Risk metrics calculation failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["has_var"] = "var_metrics" in result
                test_results["has_sharpe"] = "sharpe_ratio" in result
                print("✅ Risk metrics integration successful")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Risk metrics test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_monte_carlo_integration(self) -> Dict[str, Any]:
        """Test Monte Carlo simulation."""
        print("\n🎲 Testing Monte Carlo Simulation Integration...")

        test_results = {
            "test_name": "monte_carlo",
            "platform": "Day 2",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test with reduced simulations for speed
            weights = [0.25, 0.25, 0.25, 0.25]

            result = await self.client.monte_carlo_simulation(
                symbols=self.test_symbols,
                weights=weights,
                num_simulations=1000,  # Reduced for testing
                time_horizon=252,
                scenarios=["bull_market", "bear_market"]
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Monte Carlo simulation failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["has_simulations"] = "simulations" in result
                test_results["num_scenarios"] = len(
                    result.get("scenarios", {}))
                print("✅ Monte Carlo simulation integration successful")
                print(
                    f"   🎲 Scenarios tested: {test_results['num_scenarios']}")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Monte Carlo test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_trading_integration(self) -> Dict[str, Any]:
        """Test Day 3 platform integration - Algorithmic Trading."""
        print("\n🚀 Testing Trading Strategy Integration (Day 3)...")

        test_results = {
            "test_name": "trading_strategy",
            "platform": "Day 3",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test momentum strategy
            result = await self.client.execute_trading_strategy(
                strategy_type="momentum",
                symbols=self.test_symbols[:2],  # Test with 2 symbols
                parameters={
                    "short_window": 20,
                    "long_window": 50,
                    "position_size": 1000
                }
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Trading strategy failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["strategy_active"] = result.get(
                    "strategy_active", False)
                test_results["has_signals"] = "signals" in result
                print("✅ Trading strategy integration successful")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Trading strategy test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_position_management(self) -> Dict[str, Any]:
        """Test position management capabilities."""
        print("\n📊 Testing Position Management Integration...")

        test_results = {
            "test_name": "position_management",
            "platform": "Day 3",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test position retrieval
            result = await self.client.manage_positions(
                action="get_all"
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Position management failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["num_positions"] = len(
                    result.get("positions", []))
                test_results["total_value"] = result.get("total_value", 0)
                print("✅ Position management integration successful")
                print(
                    f"   📊 Positions tracked: {test_results['num_positions']}")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Position management test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_cross_platform_intelligence(self) -> Dict[str, Any]:
        """Test unified cross-platform intelligence."""
        print("\n🧠 Testing Cross-Platform Intelligence Integration...")

        test_results = {
            "test_name": "cross_platform_intelligence",
            "platform": "Unified (Day 4)",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test comprehensive financial insights
            result = await self.client.generate_financial_insights(
                symbols=self.test_symbols,
                analysis_scope="comprehensive",
                context={
                    "portfolio_value": 100000,
                    "risk_tolerance": "moderate",
                    "time_horizon": "long_term"
                }
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(
                    f"❌ Cross-platform intelligence failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["has_insights"] = "insights" in result
                test_results["has_recommendations"] = "recommendations" in result
                test_results["platforms_integrated"] = len(
                    result.get("platform_data", {}))
                print("✅ Cross-platform intelligence integration successful")
                print(
                    f"   🔗 Platforms integrated: {test_results['platforms_integrated']}")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Cross-platform intelligence test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_rebalancing_advice(self) -> Dict[str, Any]:
        """Test portfolio rebalancing advice."""
        print("\n🔄 Testing Portfolio Rebalancing Advice...")

        test_results = {
            "test_name": "rebalancing_advice",
            "platform": "Unified (Day 4)",
            "status": "running",
            "start_time": time.time()
        }

        try:
            # Test rebalancing advice
            current_portfolio = {
                "AAPL": 0.4,
                "MSFT": 0.3,
                "GOOGL": 0.2,
                "TSLA": 0.1
            }

            result = await self.client.portfolio_rebalancing_advice(
                current_portfolio=current_portfolio,
                rebalancing_frequency="quarterly",
                transaction_cost=0.001
            )

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Rebalancing advice failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["has_advice"] = "advice" in result
                test_results["rebalance_needed"] = result.get(
                    "rebalance_needed", False)
                print("✅ Rebalancing advice integration successful")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Rebalancing advice test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def test_health_check(self) -> Dict[str, Any]:
        """Test MCP server health check."""
        print("\n🏥 Testing MCP Server Health Check...")

        test_results = {
            "test_name": "health_check",
            "platform": "MCP Server",
            "status": "running",
            "start_time": time.time()
        }

        try:
            result = await self.client.health_check()

            # Validate response
            if "error" in result:
                test_results["status"] = "failed"
                test_results["error"] = result["error"]
                print(f"❌ Health check failed: {result['error']}")
            else:
                test_results["status"] = "passed"
                test_results["server_healthy"] = result.get("healthy", False)
                test_results["uptime"] = result.get("uptime", 0)
                print("✅ MCP server health check successful")
                print(f"   💚 Server healthy: {test_results['server_healthy']}")

        except Exception as e:
            test_results["status"] = "error"
            test_results["exception"] = str(e)
            print(f"❌ Health check test error: {e}")

        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - \
            test_results["start_time"]

        return test_results

    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete MCP integration test suite."""
        print("🧪 Starting Comprehensive MCP Integration Test Suite")
        print("=" * 60)

        suite_start_time = time.time()

        # Setup
        setup_success = await self.setup()
        if not setup_success:
            return {"error": "Setup failed", "status": "failed"}

        # Run all tests
        test_functions = [
            self.test_health_check,
            self.test_market_analysis_integration,
            self.test_portfolio_optimization_integration,
            self.test_risk_metrics_integration,
            self.test_monte_carlo_integration,
            self.test_trading_integration,
            self.test_position_management,
            self.test_cross_platform_intelligence,
            self.test_rebalancing_advice
        ]

        test_results = []
        passed_tests = 0
        failed_tests = 0

        for test_func in test_functions:
            try:
                result = await test_func()
                test_results.append(result)

                if result["status"] == "passed":
                    passed_tests += 1
                else:
                    failed_tests += 1

            except Exception as e:
                print(f"❌ Test function {test_func.__name__} failed: {e}")
                failed_tests += 1
                test_results.append({
                    "test_name": test_func.__name__,
                    "status": "error",
                    "exception": str(e)
                })

        # Cleanup
        await self.client.disconnect()

        suite_end_time = time.time()
        suite_duration = suite_end_time - suite_start_time

        # Summary
        print("\n" + "=" * 60)
        print("🏁 Test Suite Complete")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️ Total Duration: {suite_duration:.2f} seconds")
        print(
            f"📊 Success Rate: {(passed_tests / (passed_tests + failed_tests) * 100):.1f}%")

        return {
            "suite_status": "completed",
            "total_tests": len(test_results),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / (passed_tests + failed_tests) * 100,
            "total_duration": suite_duration,
            "test_results": test_results
        }


async def main():
    """Main test execution function."""
    tester = MCPIntegrationTester()
    results = await tester.run_comprehensive_test_suite()

    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📁 Full test results saved to: test_results.json")

    return results


if __name__ == "__main__":
    # Run the comprehensive test suite
    results = asyncio.run(main())

    # Exit with appropriate code
    if results.get("failed_tests", 1) > 0:
        exit(1)
    else:
        exit(0)
