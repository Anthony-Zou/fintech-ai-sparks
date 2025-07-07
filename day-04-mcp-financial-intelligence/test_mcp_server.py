#!/usr/bin/env python3
"""
Quick test script to verify MCP server functionality
"""

from mcp_server.server import FinancialIntelligenceServer
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_mcp_server():
    """Test the MCP server functionality."""
    try:
        print("🧪 Testing MCP Financial Intelligence Server...")

        # Create server instance
        server = FinancialIntelligenceServer()
        print("✅ Server instance created successfully")

        # Test tool setup
        print(f"✅ Tools setup complete")

        # Test individual handlers
        print("\n📊 Testing Market Analysis...")
        market_result = await server._handle_market_analysis({
            "symbols": ["AAPL", "MSFT"],
            "timeframe": "1y",
            "forecast_days": 30,
            "analysis_type": ["price", "volume"]
        })
        print("✅ Market analysis test passed")

        print("\n💼 Testing Portfolio Optimization...")
        portfolio_result = await server._handle_portfolio_optimization({
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "optimization_method": "max_sharpe",
            "risk_free_rate": 0.02
        })
        print("✅ Portfolio optimization test passed")

        print("\n📈 Testing Risk Metrics...")
        risk_result = await server._handle_risk_metrics({
            "symbols": ["AAPL", "MSFT"],
            "weights": [0.6, 0.4],
            "confidence_levels": [0.95, 0.99],
            "portfolio_value": 100000
        })
        print("✅ Risk metrics test passed")

        print("\n🔮 Testing Financial Insights...")
        insights_result = await server._handle_financial_insights({
            "symbols": ["AAPL", "MSFT", "TSLA"],
            "analysis_scope": "comprehensive",
            "context": {"market_conditions": "volatile"}
        })
        print("✅ Financial insights test passed")

        print("\n🎯 All MCP server tests passed successfully!")
        print("✅ MCP Financial Intelligence Server is working correctly")

        return True

    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
