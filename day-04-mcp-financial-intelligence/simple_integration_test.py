#!/usr/bin/env python3
"""
Simple MCP Financial Intelligence Platform Integration Test

Direct testing of MCP server functionality without stdio client complexity.
"""

import asyncio
import json
import time
from typing import Dict, Any
from mcp_server.server import FinancialIntelligenceServer


class SimpleMCPIntegrationTest:
    """Simple integration test for MCP server functionality."""

    def __init__(self):
        self.server = None
        self.test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        self.test_results = {}

    async def setup(self) -> bool:
        """Setup test environment."""
        print("🚀 Setting up Simple MCP Integration Test...")

        try:
            # Create server instance
            self.server = FinancialIntelligenceServer()
            print("✅ MCP server instance created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create MCP server: {e}")
            return False

    async def test_market_analysis(self) -> Dict[str, Any]:
        """Test market analysis functionality."""
        print("\n📊 Testing Market Analysis...")

        start_time = time.time()
        test_result = {
            "test_name": "market_analysis",
            "status": "running",
            "start_time": start_time
        }

        try:
            result = await self.server._handle_market_analysis({
                "symbols": self.test_symbols[:2],
                "timeframe": "1y",
                "forecast_days": 30,
                "analysis_type": ["price", "volume"]
            })

            # Parse JSON result
            data = json.loads(result)

            test_result.update({
                "status": "passed",
                "symbols_analyzed": len(data.get("symbols_analyzed", [])),
                "has_forecasts": "forecasts" in data,
                "has_recommendations": "recommendations" in data,
                "response_size": len(result)
            })

            print(f"✅ Market analysis test passed")
            print(f"   📊 Analyzed {test_result['symbols_analyzed']} symbols")
            print(f"   📈 Forecasts: {test_result['has_forecasts']}")
            print(
                f"   💡 Recommendations: {test_result['has_recommendations']}")

        except Exception as e:
            test_result.update({
                "status": "failed",
                "error": str(e)
            })
            print(f"❌ Market analysis test failed: {e}")

        test_result["duration"] = time.time() - start_time
        return test_result

    async def test_portfolio_optimization(self) -> Dict[str, Any]:
        """Test portfolio optimization functionality."""
        print("\n💼 Testing Portfolio Optimization...")

        start_time = time.time()
        test_result = {
            "test_name": "portfolio_optimization",
            "status": "running",
            "start_time": start_time
        }

        try:
            result = await self.server._handle_portfolio_optimization({
                "symbols": self.test_symbols,
                "optimization_method": "max_sharpe",
                "risk_free_rate": 0.02,
                "constraints": {},
                "views": {}
            })

            data = json.loads(result)

            test_result.update({
                "status": "passed",
                "has_weights": "optimal_weights" in data,
                "has_metrics": "portfolio_metrics" in data,
                "optimization_method": data.get("method"),
                "num_assets": len(data.get("symbols", []))
            })

            print(f"✅ Portfolio optimization test passed")
            print(f"   ⚖️ Method: {test_result['optimization_method']}")
            print(f"   📊 Assets: {test_result['num_assets']}")
            print(f"   🎯 Has weights: {test_result['has_weights']}")

        except Exception as e:
            test_result.update({
                "status": "failed",
                "error": str(e)
            })
            print(f"❌ Portfolio optimization test failed: {e}")

        test_result["duration"] = time.time() - start_time
        return test_result

    async def test_risk_metrics(self) -> Dict[str, Any]:
        """Test risk metrics calculation."""
        print("\n📈 Testing Risk Metrics...")

        start_time = time.time()
        test_result = {
            "test_name": "risk_metrics",
            "status": "running",
            "start_time": start_time
        }

        try:
            result = await self.server._handle_risk_metrics({
                "symbols": self.test_symbols,
                "weights": [0.25, 0.25, 0.25, 0.25],
                "confidence_levels": [0.95, 0.99],
                "portfolio_value": 100000
            })

            data = json.loads(result)

            test_result.update({
                "status": "passed",
                "has_var": "value_at_risk" in data.get("risk_metrics", {}),
                "has_sharpe": "sharpe_ratio" in data.get("risk_metrics", {}).get("performance_ratios", {}),
                "portfolio_value": data.get("portfolio_value"),
                "confidence_levels": len(data.get("risk_metrics", {}).get("value_at_risk", {}))
            })

            print(f"✅ Risk metrics test passed")
            print(f"   💰 Portfolio value: ${test_result['portfolio_value']:,}")
            print(f"   📊 VaR levels: {test_result['confidence_levels']}")
            print(f"   📈 Has Sharpe ratio: {test_result['has_sharpe']}")

        except Exception as e:
            test_result.update({
                "status": "failed",
                "error": str(e)
            })
            print(f"❌ Risk metrics test failed: {e}")

        test_result["duration"] = time.time() - start_time
        return test_result

    async def test_financial_insights(self) -> Dict[str, Any]:
        """Test unified financial insights."""
        print("\n🔮 Testing Financial Insights...")

        start_time = time.time()
        test_result = {
            "test_name": "financial_insights",
            "status": "running",
            "start_time": start_time
        }

        try:
            result = await self.server._handle_financial_insights({
                "symbols": self.test_symbols,
                "analysis_scope": "comprehensive",
                "context": {"market_condition": "volatile"}
            })

            data = json.loads(result)

            test_result.update({
                "status": "passed",
                "has_insights": "unified_insights" in data,
                "has_recommendations": "recommendations" in data.get("unified_insights", {}),
                "symbols_analyzed": len(data.get("symbols_analyzed", [])),
                "market_outlook": data.get("unified_insights", {}).get("market_outlook")
            })

            print(f"✅ Financial insights test passed")
            print(f"   🔍 Symbols analyzed: {test_result['symbols_analyzed']}")
            print(f"   📊 Market outlook: {test_result['market_outlook']}")
            print(
                f"   💡 Has recommendations: {test_result['has_recommendations']}")

        except Exception as e:
            test_result.update({
                "status": "failed",
                "error": str(e)
            })
            print(f"❌ Financial insights test failed: {e}")

        test_result["duration"] = time.time() - start_time
        return test_result

    async def test_trading_functionality(self) -> Dict[str, Any]:
        """Test trading strategy and position management."""
        print("\n🎯 Testing Trading Functionality...")

        start_time = time.time()
        test_result = {
            "test_name": "trading_functionality",
            "status": "running",
            "start_time": start_time
        }

        try:
            # Test trading strategy
            strategy_result = await self.server._handle_trading_strategy({
                "strategy_type": "momentum",
                "symbols": self.test_symbols[:2],
                "parameters": {"lookback_period": 20, "threshold": 0.02},
                "execution_mode": "simulation"
            })

            # Test position management
            position_result = await self.server._handle_position_management({
                "action": "get_positions"
            })

            strategy_data = json.loads(strategy_result)
            position_data = json.loads(position_result)

            test_result.update({
                "status": "passed",
                "strategy_executed": "execution_timestamp" in strategy_data,
                "has_positions": "positions" in position_data,
                "strategy_type": strategy_data.get("strategy_type"),
                "execution_mode": strategy_data.get("execution_mode")
            })

            print(f"✅ Trading functionality test passed")
            print(f"   📊 Strategy: {test_result['strategy_type']}")
            print(f"   🔧 Mode: {test_result['execution_mode']}")
            print(f"   💼 Has positions: {test_result['has_positions']}")

        except Exception as e:
            test_result.update({
                "status": "failed",
                "error": str(e)
            })
            print(f"❌ Trading functionality test failed: {e}")

        test_result["duration"] = time.time() - start_time
        return test_result

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        print("🧪 Starting Simple MCP Integration Test Suite")
        print("=" * 60)

        # Setup
        setup_success = await self.setup()
        if not setup_success:
            return {"status": "failed", "error": "Setup failed"}

        # Run all tests
        results = {
            "test_suite": "simple_mcp_integration",
            "start_time": time.time(),
            "tests": {}
        }

        tests = [
            self.test_market_analysis,
            self.test_portfolio_optimization,
            self.test_risk_metrics,
            self.test_financial_insights,
            self.test_trading_functionality
        ]

        for test in tests:
            test_result = await test()
            results["tests"][test_result["test_name"]] = test_result

        # Summary
        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]

        passed_tests = sum(
            1 for test in results["tests"].values() if test["status"] == "passed")
        total_tests = len(results["tests"])

        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests * 100
        }

        print("\n" + "=" * 60)
        print("🎯 Test Suite Summary")
        print("=" * 60)
        print(f"📊 Total tests: {results['summary']['total_tests']}")
        print(f"✅ Passed: {results['summary']['passed_tests']}")
        print(f"❌ Failed: {results['summary']['failed_tests']}")
        print(f"📈 Success rate: {results['summary']['success_rate']:.1f}%")
        print(f"⏱️ Total duration: {results['total_duration']:.2f}s")

        if results['summary']['success_rate'] == 100:
            print(
                "\n🎉 All tests passed! MCP Financial Intelligence Platform is working correctly!")
        else:
            print("\n⚠️ Some tests failed. Check the detailed results above.")

        # Save results
        with open("simple_test_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n📁 Detailed results saved to: simple_test_results.json")

        return results


async def main():
    """Main test runner."""
    tester = SimpleMCPIntegrationTest()
    results = await tester.run_all_tests()

    # Exit with appropriate code
    success_rate = results.get("summary", {}).get("success_rate", 0)
    exit_code = 0 if success_rate == 100 else 1

    return exit_code

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
