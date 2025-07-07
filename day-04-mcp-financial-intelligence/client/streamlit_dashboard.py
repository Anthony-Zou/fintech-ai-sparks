"""
MCP Financial Intelligence Dashboard (Fixed Version)

Unified Streamlit dashboard that directly uses the working MCP server
without the problematic stdio client connection.
"""

from mcp_server.server import FinancialIntelligenceServer
import streamlit as st
import asyncio
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import time
import sys
from pathlib import Path

# Add project root to path to import server directly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the working MCP server directly

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="MCP Financial Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .tool-status {
        background: #e3f2fd;
        padding: 0.5rem;
        border-radius: 6px;
        border: 1px solid #2196f3;
        margin: 0.5rem 0;
    }
    .sidebar-section {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
    st.session_state.mcp_server = None
    st.session_state.available_tools = [
        "analyze_market_trends",
        "optimize_portfolio",
        "calculate_risk_metrics",
        "monte_carlo_simulation",
        "execute_trading_strategy",
        "manage_positions",
        "generate_financial_insights",
        "portfolio_rebalancing_advice"
    ]
    st.session_state.analysis_results = {}
    st.session_state.portfolio_data = {}
    st.session_state.trading_data = {}

# Title and description
st.markdown("""
<div class="main-header">
    <h1>🚀 MCP Financial Intelligence Platform</h1>
    <p>Cutting-edge AI-powered financial analysis using Model Context Protocol (MCP) integration</p>
    <p><strong>Unified Intelligence:</strong> Market Analysis • Portfolio Optimization • Algorithmic Trading</p>
</div>
""", unsafe_allow_html=True)

# Async function wrappers for Streamlit


def run_async(coro):
    """Run async function in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


async def connect_to_mcp_server():
    """Connect to MCP server directly."""
    try:
        server = FinancialIntelligenceServer()
        return True, server
    except Exception as e:
        logger.error(f"Error creating MCP server: {e}")
        return False, None


async def call_mcp_tool_direct(server, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call MCP tool directly on server."""
    try:
        if tool_name == "analyze_market_trends":
            result = await server._handle_market_analysis(arguments)
        elif tool_name == "optimize_portfolio":
            result = await server._handle_portfolio_optimization(arguments)
        elif tool_name == "calculate_risk_metrics":
            result = await server._handle_risk_metrics(arguments)
        elif tool_name == "monte_carlo_simulation":
            result = await server._handle_monte_carlo(arguments)
        elif tool_name == "execute_trading_strategy":
            result = await server._handle_trading_strategy(arguments)
        elif tool_name == "manage_positions":
            result = await server._handle_position_management(arguments)
        elif tool_name == "generate_financial_insights":
            result = await server._handle_financial_insights(arguments)
        elif tool_name == "portfolio_rebalancing_advice":
            result = await server._handle_rebalancing_advice(arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

        # Parse JSON result
        return json.loads(result)
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return {"error": str(e)}

# Sidebar - MCP Connection and Configuration
with st.sidebar:
    st.markdown("## 🔗 MCP Connection")

    if st.button("🚀 Connect to MCP Server", type="primary"):
        with st.spinner("Connecting to MCP Financial Intelligence Server..."):
            try:
                connected, server = run_async(connect_to_mcp_server())
                if connected:
                    st.session_state.mcp_connected = True
                    st.session_state.mcp_server = server
                    st.success("✅ Connected to MCP Server!")
                    st.markdown(
                        f"**Available Tools:** {len(st.session_state.available_tools)}")
                else:
                    st.error("❌ Failed to connect to MCP Server")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")

    # Display connection status
    if st.session_state.mcp_connected:
        st.markdown("""
        <div class="success-card">
            <strong>🟢 MCP Server Connected</strong><br>
            Ready for financial intelligence operations
        </div>
        """, unsafe_allow_html=True)

        # Show available tools
        with st.expander("📋 Available MCP Tools"):
            for tool in st.session_state.available_tools:
                st.markdown(
                    f"<div class='tool-status'>🔧 {tool}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Platform Selection
    st.markdown("## 🎯 Platform Selection")
    selected_platforms = st.multiselect(
        "Select Financial Platforms:",
        ["Day 1: Market Analysis", "Day 2: Portfolio Risk",
            "Day 3: Algorithmic Trading"],
        default=["Day 1: Market Analysis", "Day 2: Portfolio Risk"]
    )

    # Global Configuration
    st.markdown("""
    <div class="sidebar-section">
        <h4>🔧 Global Configuration</h4>
    </div>
    """, unsafe_allow_html=True)

    # Common symbols
    default_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    symbols_input = st.text_area(
        "📊 Trading Symbols:",
        value=", ".join(default_symbols),
        help="Enter symbols separated by commas"
    )
    symbols = [s.strip().upper()
               for s in symbols_input.split(",") if s.strip()]

    # Portfolio value
    portfolio_value = st.number_input(
        "💰 Portfolio Value ($):",
        min_value=1000,
        max_value=10000000,
        value=100000,
        step=10000
    )

# Main dashboard tabs
if st.session_state.mcp_connected:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Intelligence",
        "⚖️ Risk Analytics",
        "🎯 Trading Engine",
        "🧠 Cross-Platform Insights",
        "🔧 MCP Control Center"
    ])

    with tab1:
        st.markdown("## 📊 Market Intelligence (Day 1 Integration)")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🔍 Market Analysis Configuration")

            timeframe = st.selectbox(
                "📅 Analysis Timeframe:",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                index=3
            )

            forecast_days = st.slider(
                "🔮 Forecast Days:",
                min_value=7,
                max_value=90,
                value=30
            )

            analysis_types = st.multiselect(
                "📈 Analysis Types:",
                ["price", "volume", "volatility"],
                default=["price", "volume"]
            )

            if st.button("🚀 Run Market Analysis", type="primary"):
                if symbols:
                    with st.spinner("Analyzing market trends..."):
                        arguments = {
                            "symbols": symbols[:3],  # Limit to 3 for demo
                            "timeframe": timeframe,
                            "forecast_days": forecast_days,
                            "analysis_type": analysis_types
                        }

                        result = run_async(call_mcp_tool_direct(
                            st.session_state.mcp_server,
                            "analyze_market_trends",
                            arguments
                        ))

                        if "error" not in result:
                            st.session_state.analysis_results = result
                            st.success("✅ Market analysis complete!")
                        else:
                            st.error(f"❌ Error: {result['error']}")
                else:
                    st.warning("⚠️ Please enter symbols first")

        with col2:
            st.markdown("### 📈 Analysis Results")

            if st.session_state.analysis_results:
                results = st.session_state.analysis_results

                # Display summary metrics
                st.markdown("#### 🎯 Summary")
                if "symbols_analyzed" in results:
                    st.metric("Symbols Analyzed", len(
                        results["symbols_analyzed"]))
                if "forecast_horizon" in results:
                    st.metric("Forecast Horizon",
                              f"{results['forecast_horizon']} days")

                # Show recommendations
                if "recommendations" in results:
                    st.markdown("#### 💡 Recommendations")
                    for rec in results["recommendations"]:
                        action_color = "🟢" if "BUY" in rec["action"] else "🔴" if "SELL" in rec["action"] else "🟡"
                        st.markdown(
                            f"{action_color} **{rec['symbol']}**: {rec['action']} (confidence: {rec['confidence']:.3f})")
            else:
                st.info("👆 Run market analysis to see results here")

    with tab2:
        st.markdown("## ⚖️ Risk Analytics (Day 2 Integration)")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🎯 Portfolio Optimization")

            optimization_method = st.selectbox(
                "🔧 Optimization Method:",
                ["max_sharpe", "min_volatility", "risk_parity", "black_litterman"]
            )

            risk_free_rate = st.slider(
                "📈 Risk-free Rate:",
                min_value=0.0,
                max_value=0.1,
                value=0.02,
                step=0.005,
                format="%.3f"
            )

            if st.button("⚖️ Optimize Portfolio", type="primary"):
                if symbols:
                    with st.spinner("Optimizing portfolio..."):
                        arguments = {
                            "symbols": symbols,
                            "optimization_method": optimization_method,
                            "risk_free_rate": risk_free_rate,
                            "constraints": {"max_weight": 0.4, "min_weight": 0.05}
                        }

                        result = run_async(call_mcp_tool_direct(
                            st.session_state.mcp_server,
                            "optimize_portfolio",
                            arguments
                        ))

                        if "error" not in result:
                            st.session_state.portfolio_data = result
                            st.success("✅ Portfolio optimization complete!")
                        else:
                            st.error(f"❌ Error: {result['error']}")

        with col2:
            st.markdown("### 📊 Portfolio Results")

            if st.session_state.portfolio_data:
                portfolio = st.session_state.portfolio_data

                # Display portfolio metrics
                if "portfolio_metrics" in portfolio:
                    metrics = portfolio["portfolio_metrics"]

                    col2a, col2b, col2c = st.columns(3)
                    with col2a:
                        st.metric("Expected Return",
                                  f"{metrics.get('expected_return', 0):.3f}")
                    with col2b:
                        st.metric("Volatility",
                                  f"{metrics.get('volatility', 0):.3f}")
                    with col2c:
                        st.metric("Sharpe Ratio",
                                  f"{metrics.get('sharpe_ratio', 0):.3f}")

                # Show optimal weights
                if "optimal_weights" in portfolio:
                    st.markdown("#### 🎯 Optimal Weights")
                    weights_df = pd.DataFrame(
                        list(portfolio["optimal_weights"].items()),
                        columns=["Symbol", "Weight"]
                    )
                    weights_df["Weight"] = weights_df["Weight"].apply(
                        lambda x: f"{x:.1%}")
                    st.dataframe(weights_df, use_container_width=True)

                    # Pie chart
                    fig = px.pie(
                        values=list(portfolio["optimal_weights"].values()),
                        names=list(portfolio["optimal_weights"].keys()),
                        title="Portfolio Allocation"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👆 Optimize portfolio to see results here")

        # Risk Metrics Section
        st.markdown("### 📈 Risk Metrics Analysis")

        col3, col4 = st.columns([1, 1])

        with col3:
            confidence_levels = st.multiselect(
                "📊 VaR Confidence Levels:",
                [0.90, 0.95, 0.99],
                default=[0.95, 0.99]
            )

            if st.button("📊 Calculate Risk Metrics", type="primary"):
                if symbols and len(symbols) > 0:
                    # Use equal weights for demo
                    equal_weights = [1.0 / len(symbols)] * len(symbols)

                    with st.spinner("Calculating risk metrics..."):
                        arguments = {
                            "symbols": symbols,
                            "weights": equal_weights,
                            "confidence_levels": confidence_levels,
                            "portfolio_value": portfolio_value
                        }

                        result = run_async(call_mcp_tool_direct(
                            st.session_state.mcp_server,
                            "calculate_risk_metrics",
                            arguments
                        ))

                        if "error" not in result:
                            st.session_state.risk_data = result
                            st.success("✅ Risk metrics calculated!")
                        else:
                            st.error(f"❌ Error: {result['error']}")

        with col4:
            if hasattr(st.session_state, 'risk_data'):
                risk_data = st.session_state.risk_data

                if "risk_metrics" in risk_data:
                    metrics = risk_data["risk_metrics"]

                    # Volatility metrics
                    if "volatility_metrics" in metrics:
                        vol = metrics["volatility_metrics"]
                        st.metric("Daily Volatility",
                                  f"{vol.get('daily_volatility', 0):.3f}")
                        st.metric("Annual Volatility",
                                  f"{vol.get('annual_volatility', 0):.3f}")

                    # VaR metrics
                    if "value_at_risk" in metrics:
                        st.markdown("#### ⚠️ Value at Risk")
                        for level, var_data in metrics["value_at_risk"].items():
                            daily_var = abs(var_data.get("daily", 0))
                            st.metric(f"VaR {level}",
                                      f"${daily_var:,.0f} daily")

    with tab3:
        st.markdown("## 🎯 Trading Engine (Day 3 Integration)")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🤖 Trading Strategy")

            strategy_type = st.selectbox(
                "📊 Strategy Type:",
                ["momentum", "mean_reversion", "pairs_trading"]
            )

            execution_mode = st.selectbox(
                "⚡ Execution Mode:",
                ["simulation", "paper_trading", "live_trading"]
            )

            if st.button("🚀 Execute Strategy", type="primary"):
                if symbols:
                    with st.spinner("Executing trading strategy..."):
                        arguments = {
                            "strategy_type": strategy_type,
                            "symbols": symbols[:3],
                            "parameters": {
                                "lookback_period": 20,
                                "threshold": 0.02,
                                "position_size": 0.1
                            },
                            "execution_mode": execution_mode
                        }

                        result = run_async(call_mcp_tool_direct(
                            st.session_state.mcp_server,
                            "execute_trading_strategy",
                            arguments
                        ))

                        if "error" not in result:
                            st.session_state.trading_data = result
                            st.success("✅ Trading strategy executed!")
                        else:
                            st.error(f"❌ Error: {result['error']}")

        with col2:
            st.markdown("### 📊 Trading Results")

            if st.session_state.trading_data:
                trading = st.session_state.trading_data

                # Strategy info
                st.metric("Strategy", trading.get("strategy_type", "N/A"))
                st.metric("Execution Mode", trading.get(
                    "execution_mode", "N/A"))

                # Recent trades
                if "recent_trades" in trading:
                    st.markdown("#### 📈 Recent Trades")
                    trades_df = pd.DataFrame(trading["recent_trades"])
                    if not trades_df.empty:
                        st.dataframe(trades_df, use_container_width=True)
            else:
                st.info("👆 Execute trading strategy to see results here")

    with tab4:
        st.markdown("## 🧠 Cross-Platform Intelligence")

        if st.button("🔮 Generate Unified Insights", type="primary"):
            if symbols:
                with st.spinner("Generating unified financial insights..."):
                    arguments = {
                        "symbols": symbols,
                        "analysis_scope": "comprehensive",
                        "context": {
                            "market_condition": "volatile",
                            "economic_outlook": "uncertain",
                            "investor_sentiment": "cautious"
                        }
                    }

                    result = run_async(call_mcp_tool_direct(
                        st.session_state.mcp_server,
                        "generate_financial_insights",
                        arguments
                    ))

                    if "error" not in result:
                        st.session_state.insights_data = result
                        st.success("✅ Unified insights generated!")
                    else:
                        st.error(f"❌ Error: {result['error']}")

        if hasattr(st.session_state, 'insights_data'):
            insights = st.session_state.insights_data

            if "unified_insights" in insights:
                unified = insights["unified_insights"]

                # Market outlook
                st.markdown("### 🎯 Market Outlook")
                st.info(f"**Outlook:** {unified.get('market_outlook', 'N/A')}")

                # Key insights
                if "key_insights" in unified:
                    st.markdown("### 💡 Key Insights")
                    for insight in unified["key_insights"]:
                        st.markdown(f"• {insight}")

                # Recommendations
                if "recommendations" in unified:
                    recs = unified["recommendations"]
                    if "immediate_actions" in recs:
                        st.markdown("### 🎯 Immediate Actions")
                        for action in recs["immediate_actions"]:
                            st.markdown(f"• {action}")

    with tab5:
        st.markdown("## 🔧 MCP Control Center")

        # Server status
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🟢 Server Status")
            st.success("MCP Server: Connected")
            st.info(
                f"Available Tools: {len(st.session_state.available_tools)}")
            st.info(f"Portfolio Value: ${portfolio_value:,}")

        with col2:
            st.markdown("### 📊 Platform Statistics")
            st.metric("Active Symbols", len(symbols))
            st.metric("Connected Platforms", len(selected_platforms))

        # Tool testing
        st.markdown("### 🧪 Tool Testing")

        test_tool = st.selectbox(
            "Select Tool to Test:",
            st.session_state.available_tools
        )

        if st.button("🧪 Test Tool"):
            st.info(f"Testing tool: {test_tool}")

            # Simple test arguments
            test_args = {
                "symbols": symbols[:2] if symbols else ["AAPL", "MSFT"],
                "timeframe": "1y",
                "forecast_days": 30
            }

            with st.spinner(f"Testing {test_tool}..."):
                result = run_async(call_mcp_tool_direct(
                    st.session_state.mcp_server,
                    test_tool,
                    test_args
                ))

                if "error" not in result:
                    st.success(f"✅ Tool {test_tool} working correctly!")
                    with st.expander("View Test Results"):
                        st.json(result)
                else:
                    st.error(f"❌ Tool test failed: {result['error']}")

else:
    # Connection required message
    st.warning(
        "🔗 Please connect to the MCP server using the sidebar to access the dashboard features.")

    st.markdown("""
    ## 🚀 MCP Financial Intelligence Platform
    
    This dashboard provides unified access to:
    
    ### 📊 Day 1: Market Analysis & Forecasting
    - Technical analysis and price forecasting
    - Volume demand predictions
    - Market trend identification
    
    ### ⚖️ Day 2: Portfolio Risk Analytics  
    - Modern Portfolio Theory optimization
    - Monte Carlo simulations
    - Value at Risk (VaR) calculations
    - Risk-adjusted performance metrics
    
    ### 🎯 Day 3: Algorithmic Trading
    - Momentum and mean-reversion strategies
    - Position management
    - Trade execution simulation
    
    ### 🧠 Unified Intelligence
    - Cross-platform data synthesis
    - AI-powered financial insights
    - Integrated decision support
    
    **🔗 Connect to MCP server to get started!**
    """)

# Footer
st.markdown("---")
st.markdown(
    "**🚀 MCP Financial Intelligence Platform** | Powered by Model Context Protocol | Built with Streamlit")
