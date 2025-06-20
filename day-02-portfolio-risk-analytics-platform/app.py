from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import warnings
import json
warnings.filterwarnings('ignore')

# Import plotting libraries with fallbacks
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    st.error("Plotly not available. Please install with: pip install plotly")
    PLOTLY_AVAILABLE = False
    go, px = None, None

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    st.error("yfinance not available. Please install with: pip install yfinance")
    YFINANCE_AVAILABLE = False
    yf = None


# Import our custom modules with error handling
try:
    from portfolio_optimizer import PortfolioOptimizer
    from risk_metrics import RiskMetrics
    from monte_carlo import MonteCarloSimulator
    MODULES_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing custom modules: {e}")
    MODULES_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Portfolio Risk Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .risk-alert {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .success-metric {
        background: #d4edda;
        border-left: 4px solid #28a745;
    }
    .warning-metric {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .danger-metric {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = None
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = None
if 'risk_calculator' not in st.session_state:
    st.session_state.risk_calculator = None
if 'mc_simulator' not in st.session_state:
    st.session_state.mc_simulator = None


def main():
    # Check dependencies
    if not PLOTLY_AVAILABLE or not YFINANCE_AVAILABLE or not MODULES_AVAILABLE:
        st.error("⚠️ Missing required dependencies. Please install all requirements.")
        st.code("pip install -r requirements.txt")
        st.stop()

    # Header
    st.markdown('<div class="main-header">📊 Portfolio Risk Analytics Platform</div>',
                unsafe_allow_html=True)

    st.markdown("""
    **Enterprise-Grade Portfolio Management** | Modern Portfolio Theory | Monte Carlo Simulations | Real-Time Risk Analytics
    """)
    # Sidebar for portfolio configuration
    with st.sidebar:
        st.header("🎯 Portfolio Configuration")

        # Check data availability first
        data_available = check_data_availability()

        if not data_available:
            st.warning("⚠️ Market data unavailable. Using demo mode.")
            demo_mode = True
        else:
            demo_mode = st.checkbox("🧪 Demo Mode (Use sample data)",
                                    help="Use generated sample data instead of real market data")

        # Asset selection
        st.subheader("Asset Selection")

        # Predefined portfolios
        portfolio_presets = {
            "Tech Growth": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
            "Balanced Mix": ["SPY", "BND", "VTI", "VXUS", "GLD"],
            "Dividend Focus": ["JNJ", "PG", "KO", "PEP", "VZ"],
            "Crypto & Tech": ["BTC-USD", "ETH-USD", "AAPL", "NVDA", "AMD"],
            "ESG Focused": ["ICLN", "ESG", "ESGU", "VSGX", "SUSL"]
        }

        selected_preset = st.selectbox(
            "Choose Portfolio Preset:",
            ["Custom"] + list(portfolio_presets.keys())
        )

        if selected_preset != "Custom":
            default_tickers = portfolio_presets[selected_preset]
        else:
            default_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

        # Manual ticker input
        tickers_input = st.text_area(
            "Enter Tickers (comma separated):",
            value=", ".join(default_tickers),
            help="Enter stock/ETF tickers separated by commas"
        )

        tickers = [ticker.strip().upper()
                   for ticker in tickers_input.split(",") if ticker.strip()]

        # Time period selection
        periods = {
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }

        selected_period = st.selectbox(
            "Historical Data Period:", list(periods.keys()), index=2)
        period = periods[selected_period]

        # Risk-free rate
        risk_free_rate = st.slider(
            "Risk-Free Rate (%)", 0.0, 5.0, 2.0, 0.1) / 100

        # Portfolio value
        portfolio_value = st.number_input(
            "Portfolio Value ($)",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=10000
        )

        # Load data button
        button_text = "🧪 Load Demo Data" if demo_mode else "🔄 Load Portfolio Data"
        if st.button(button_text, type="primary"):
            with st.spinner("Loading portfolio data..."):
                try:
                    if demo_mode:
                        # Generate demo data
                        dates = pd.date_range(
                            '2022-01-01', '2024-12-31', freq='D')
                        np.random.seed(42)

                        # Create synthetic price data
                        price_data = pd.DataFrame(index=dates)
                        for i, ticker in enumerate(tickers):
                            # Different characteristics for each asset
                            drift = 0.0005 + i * 0.0002
                            volatility = 0.015 + i * 0.005
                            returns = np.random.normal(
                                drift, volatility, len(dates))
                            price_data[ticker] = 100 * (1 + returns).cumprod()
                        returns_data = price_data.pct_change().dropna()

                        # Initialize modules with demo data
                        optimizer = PortfolioOptimizer(
                            returns_data, risk_free_rate)
                        risk_calculator = RiskMetrics(
                            returns_data, risk_free_rate)
                        mc_simulator = MonteCarloSimulator(
                            returns_data, num_simulations=5000, risk_free_rate=risk_free_rate)

                        st.success(
                            f"✅ Demo data loaded for {len(tickers)} assets")

                    else:
                        # Real market data
                        if not YFINANCE_AVAILABLE:
                            st.error(
                                "yfinance not available for real market data")
                            return

                        try:
                            # Fetch data using yfinance
                            data = yf.download(
                                tickers, period=period, progress=False)

                            if data.empty:
                                st.error(
                                    "No data available for selected tickers")
                                return

                            # Handle single vs multiple tickers
                            if len(tickers) == 1:
                                price_data = pd.DataFrame(data['Adj Close'])
                                price_data.columns = tickers
                            else:
                                # Check if 'Adj Close' is available
                                if 'Adj Close' in data.columns:
                                    price_data = data['Adj Close']
                                else:
                                    st.error(
                                        "Expected 'Adj Close' column not found in data")
                                    return

                            # Handle missing data
                            price_data = price_data.dropna()
                            if price_data.empty:
                                st.error(
                                    "No data available for selected tickers after cleaning")
                                return

                            returns_data = price_data.pct_change().dropna()

                            optimizer = PortfolioOptimizer(
                                returns_data, risk_free_rate)
                            risk_calculator = RiskMetrics(
                                returns_data, risk_free_rate)
                            mc_simulator = MonteCarloSimulator(
                                returns_data, num_simulations=10000, risk_free_rate=risk_free_rate)

                            st.success(
                                f"✅ Market data loaded for {len(tickers)} assets")
                        except Exception as e:
                            st.error(
                                f"Error downloading market data: {str(e)}")
                            st.info("Try using Demo Mode instead")
                            return

                    # Store in session state
                    st.session_state.portfolio_data = {
                        'prices': price_data,
                        'returns': returns_data,
                        'tickers': tickers,
                        'period': period,
                        'portfolio_value': portfolio_value,
                        'demo_mode': demo_mode
                    }
                    st.session_state.optimizer = optimizer
                    st.session_state.risk_calculator = risk_calculator
                    st.session_state.mc_simulator = mc_simulator

                except Exception as e:
                    st.error(f"❌ Error loading data: {str(e)}")
                    if not demo_mode:
                        st.info("💡 Try enabling Demo Mode to use sample data")
    # Main content area
    if st.session_state.portfolio_data is not None:

        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Portfolio Builder",
            "⚠️ Risk Dashboard",
            "📈 Monitoring & Simulation",
            "📋 Reports & Export"
        ])

        with tab1:
            portfolio_builder_tab()

        with tab2:
            risk_dashboard_tab()

        with tab3:
            monitoring_simulation_tab()

        with tab4:
            reports_export_tab()

    else:
        # Landing page when no data is loaded
        st.markdown("""
        ### 🚀 Welcome to the Portfolio Risk Analytics Platform
        
        **What makes this platform enterprise-grade:**
        
        #### 🎯 **Advanced Portfolio Optimization**
        - Modern Portfolio Theory implementation
        - Black-Litterman model with analyst views
        - Risk parity optimization
        - Efficient frontier analysis
        
        #### ⚠️ **Institutional Risk Metrics**
        - Value at Risk (VaR) - Multiple methodologies
        - Expected Shortfall (Conditional VaR)
        - Maximum Drawdown analysis
        - Sharpe, Sortino, Treynor ratios
        
        #### 🎲 **Monte Carlo Simulations**
        - 10,000+ scenario stress testing
        - Market crash simulations
        - Portfolio path analysis
        - Confidence interval predictions
        
        #### 📊 **Real-Time Analytics**
        - Live performance tracking
        - Dynamic rebalancing alerts
        - Correlation analysis
        - Professional reporting
        
        **👈 Start by configuring your portfolio in the sidebar**
        """)

        # Add sample portfolio performance chart
        create_sample_chart()


def portfolio_builder_tab():
    st.header("📊 Portfolio Construction & Optimization")

    optimizer = st.session_state.optimizer
    portfolio_data = st.session_state.portfolio_data

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Optimization Objectives")

        optimization_type = st.selectbox(
            "Select Optimization Strategy:",
            [
                "Maximum Sharpe Ratio",
                "Minimum Volatility",
                "Risk Parity",
                "Black-Litterman with Views",
                "Equal Weights"
            ]
        )

        # Constraints
        st.subheader("⚙️ Portfolio Constraints")
        max_weight = st.slider("Maximum Asset Weight (%)", 10, 100, 40) / 100
        min_weight = st.slider("Minimum Asset Weight (%)", 0, 10, 0) / 100
        # Run optimization
        if st.button("🚀 Optimize Portfolio", type="primary"):
            with st.spinner("Optimizing portfolio..."):
                try:
                    constraints = {'max_weight': max_weight,
                                   'min_weight': min_weight}

                    if optimization_type == "Maximum Sharpe Ratio":
                        result = optimizer.max_sharpe_optimization(constraints)
                    elif optimization_type == "Minimum Volatility":
                        result = optimizer.min_volatility_optimization(
                            constraints)
                    elif optimization_type == "Risk Parity":
                        result = optimizer.risk_parity_optimization()
                    elif optimization_type == "Equal Weights":
                        n_assets = len(portfolio_data['tickers'])
                        weights = np.array([1/n_assets] * n_assets)
                        result = optimizer.portfolio_stats(weights)
                    else:  # Black-Litterman
                        result = optimizer.black_litterman_optimization()

                    st.session_state.current_portfolio = result
                    st.success("✅ Portfolio optimized successfully!")

                except Exception as e:
                    st.error(f"❌ Optimization failed: {str(e)}")
                    st.error("🔧 Try with demo mode or different constraints")

    with col2:
        st.subheader("📈 Efficient Frontier")

        if st.button("Generate Efficient Frontier"):
            with st.spinner("Calculating efficient frontier..."):
                try:
                    efficient_portfolios = optimizer.efficient_frontier(50)

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=efficient_portfolios['volatility'],
                        y=efficient_portfolios['return'],
                        mode='markers+lines',
                        name='Efficient Frontier',
                        line=dict(color='blue', width=3),
                        marker=dict(size=6)
                    ))

                    fig.update_layout(
                        title="Portfolio Efficient Frontier",
                        xaxis_title="Volatility (Risk)",
                        yaxis_title="Expected Return",
                        height=400,
                        showlegend=True
                    )

                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error generating efficient frontier: {str(e)}")

    # Display current portfolio if optimized
    if 'current_portfolio' in st.session_state:
        st.subheader("🎯 Optimized Portfolio Allocation")

        result = st.session_state.current_portfolio
        weights = result['weights']
        tickers = portfolio_data['tickers']

        # Portfolio metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Expected Return",
                f"{result['return']:.2%}",
                help="Annualized expected return"
            )

        with col2:
            st.metric(
                "Volatility",
                f"{result['volatility']:.2%}",
                help="Annualized volatility (risk)"
            )

        with col3:
            st.metric(
                "Sharpe Ratio",
                f"{result['sharpe_ratio']:.3f}",
                help="Risk-adjusted return metric"
            )

        with col4:
            portfolio_value = portfolio_data['portfolio_value']
            st.metric(
                "Portfolio Value",
                f"${portfolio_value:,.0f}",
                help="Total portfolio value"
            )

        # Allocation pie chart and table
        col1, col2 = st.columns([1, 1])

        with col1:
            # Pie chart
            fig = go.Figure(data=[go.Pie(
                labels=tickers,
                values=weights,
                hole=0.4,
                textinfo='label+percent',
                textposition='auto'
            )])

            fig.update_layout(
                title="Portfolio Allocation",
                height=400,
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Allocation table
            allocation_df = pd.DataFrame({
                'Asset': tickers,
                'Weight': [f"{w:.2%}" for w in weights],
                'Value': [f"${portfolio_value * w:,.0f}" for w in weights]
            })

            st.dataframe(allocation_df, hide_index=True,
                         use_container_width=True)

            # Portfolio summary
            if hasattr(optimizer, 'get_portfolio_summary'):
                summary_df = optimizer.get_portfolio_summary(weights)
                st.subheader("📋 Detailed Portfolio Summary")
                st.dataframe(summary_df, use_container_width=True)


def risk_dashboard_tab():
    st.header("⚠️ Risk Analytics Dashboard")

    if 'current_portfolio' not in st.session_state:
        st.warning(
            "⚠️ Please optimize a portfolio first in the Portfolio Builder tab")
        return

    risk_calculator = st.session_state.risk_calculator
    weights = st.session_state.current_portfolio['weights']
    portfolio_data = st.session_state.portfolio_data

    # Risk metrics calculation
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Key Risk Metrics")

        try:
            # Calculate comprehensive risk metrics
            risk_summary = risk_calculator.risk_metrics_summary(weights)

            # Display key metrics in cards
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

            with metrics_col1:
                var_95 = risk_summary.get('VaR_1D', 0)
                color_class = "danger-metric" if var_95 < - \
                    0.05 else "warning-metric" if var_95 < -0.02 else "success-metric"

                st.markdown(f"""
                <div class="metric-card {color_class}">
                    <h4>Value at Risk (95%)</h4>
                    <h2>{var_95:.2%}</h2>
                    <p>Daily potential loss</p>
                </div>
                """, unsafe_allow_html=True)

            with metrics_col2:
                sharpe = risk_summary.get('sharpe_ratio', 0)
                color_class = "success-metric" if sharpe > 1 else "warning-metric" if sharpe > 0.5 else "danger-metric"

                st.markdown(f"""
                <div class="metric-card {color_class}">
                    <h4>Sharpe Ratio</h4>
                    <h2>{sharpe:.3f}</h2>
                    <p>Risk-adjusted return</p>
                </div>
                """, unsafe_allow_html=True)

            with metrics_col3:
                max_dd = risk_summary.get('max_drawdown', 0)
                color_class = "success-metric" if max_dd > - \
                    0.1 else "warning-metric" if max_dd > -0.2 else "danger-metric"

                st.markdown(f"""
                <div class="metric-card {color_class}">
                    <h4>Maximum Drawdown</h4>
                    <h2>{max_dd:.2%}</h2>
                    <p>Worst peak-to-trough loss</p>
                </div>
                """, unsafe_allow_html=True)

            # Detailed risk metrics table
            st.subheader("📋 Comprehensive Risk Analysis")

            detailed_metrics = {
                "Metric": [
                    "Annual Return", "Annual Volatility", "Sharpe Ratio", "Sortino Ratio",
                    "VaR (1 Day, 95%)", "VaR (1 Week, 95%)", "VaR (1 Month, 95%)",
                    "Expected Shortfall (95%)", "Maximum Drawdown", "Current Drawdown"
                ],
                "Value": [
                    f"{risk_summary.get('annual_return', 0):.2%}",
                    f"{risk_summary.get('annual_volatility', 0):.2%}",
                    f"{risk_summary.get('sharpe_ratio', 0):.3f}",
                    f"{risk_summary.get('sortino_ratio', 0):.3f}",
                    f"{risk_summary.get('VaR_1D', 0):.2%}",
                    f"{risk_summary.get('VaR_1W', 0):.2%}",
                    f"{risk_summary.get('VaR_1M', 0):.2%}",
                    f"{risk_summary.get('ES_1D', 0):.2%}",
                    f"{risk_summary.get('max_drawdown', 0):.2%}",
                    f"{risk_summary.get('current_drawdown', 0):.2%}"
                ]
            }

            metrics_df = pd.DataFrame(detailed_metrics)
            st.dataframe(metrics_df, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Error calculating risk metrics: {str(e)}")

    with col2:
        st.subheader("🔥 Risk Alerts")

        try:
            # Generate risk alerts based on metrics
            alerts = []

            if risk_summary.get('VaR_1D', 0) < -0.05:
                alerts.append("🚨 High daily VaR detected (>5%)")

            if risk_summary.get('sharpe_ratio', 0) < 0.5:
                alerts.append("⚠️ Low Sharpe ratio (<0.5)")

            if risk_summary.get('max_drawdown', 0) < -0.3:
                alerts.append("🚨 High maximum drawdown (>30%)")

            if risk_summary.get('annual_volatility', 0) > 0.4:
                alerts.append("⚠️ High portfolio volatility (>40%)")

            if not alerts:
                alerts.append("✅ Portfolio risk levels acceptable")

            for alert in alerts:
                st.markdown(f"""
                <div class="risk-alert">
                    {alert}
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Unable to generate risk alerts: {str(e)}")

    # Correlation heatmap
    st.subheader("🔗 Asset Correlation Analysis")

    try:
        correlation_matrix = risk_calculator.correlation_analysis()

        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))

        fig.update_layout(
            title="Asset Correlation Matrix",
            height=500,
            xaxis_title="Assets",
            yaxis_title="Assets"
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating correlation heatmap: {str(e)}")

    # Volatility decomposition
    st.subheader("📊 Risk Contribution Analysis")

    try:
        vol_decomp = risk_calculator.volatility_decomposition(weights)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=vol_decomp['Asset'],
            y=vol_decomp['Risk_Contribution_Pct'],
            name='Risk Contribution',
            marker_color='lightcoral'
        ))

        fig.add_trace(go.Scatter(
            x=vol_decomp['Asset'],
            y=vol_decomp['Weight'],
            mode='markers+lines',
            name='Portfolio Weight',
            marker=dict(size=10, color='blue'),
            yaxis='y2'
        ))

        fig.update_layout(
            title="Risk Contribution vs Portfolio Weight",
            xaxis_title="Assets",
            yaxis_title="Risk Contribution (%)",
            yaxis2=dict(
                title="Portfolio Weight",
                overlaying='y',
                side='right'
            ),
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating risk contribution chart: {str(e)}")


def monitoring_simulation_tab():
    st.header("📈 Portfolio Monitoring & Monte Carlo Simulation")

    if 'current_portfolio' not in st.session_state:
        st.warning(
            "⚠️ Please optimize a portfolio first in the Portfolio Builder tab")
        return

    mc_simulator = st.session_state.mc_simulator
    weights = st.session_state.current_portfolio['weights']
    portfolio_data = st.session_state.portfolio_data

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎲 Monte Carlo Simulation")

        # Simulation parameters
        sim_col1, sim_col2, sim_col3 = st.columns(3)

        with sim_col1:
            time_horizon = st.selectbox(
                "Time Horizon:",
                [30, 60, 90, 180, 252, 500],
                index=4,
                format_func=lambda x: f"{x} days ({x/252:.1f} years)" if x >= 252 else f"{x} days"
            )

        with sim_col2:
            initial_value = st.number_input(
                "Initial Value ($):",
                min_value=1000,
                max_value=10000000,
                value=portfolio_data['portfolio_value'],
                step=10000
            )

        with sim_col3:
            num_paths_display = st.selectbox(
                "Paths to Display:",
                [100, 500, 1000, 2000],
                index=1
            )

        if st.button("🚀 Run Monte Carlo Simulation", type="primary"):
            with st.spinner("Running simulations..."):
                try:
                    # Generate price paths
                    mc_results = mc_simulator.generate_price_paths(
                        weights, time_horizon, initial_value
                    )

                    # Calculate risk metrics
                    risk_metrics = mc_simulator.calculate_risk_metrics_mc(
                        weights, [0.90, 0.95,
                                  0.99], time_horizon, initial_value
                    )

                    st.session_state.mc_results = mc_results
                    st.session_state.mc_risk_metrics = risk_metrics

                    st.success("✅ Simulation completed successfully!")

                except Exception as e:
                    st.error(f"❌ Simulation failed: {str(e)}")

    with col2:
        st.subheader("📊 Simulation Settings")

        # Scenario analysis
        scenarios_to_run = st.multiselect(
            "Stress Test Scenarios:",
            ['bull_market', 'bear_market', 'high_volatility',
                'recession', 'market_crash', 'recovery'],
            default=['bear_market', 'market_crash']
        )

        if st.button("🧪 Run Stress Tests"):
            with st.spinner("Running stress tests..."):
                try:
                    scenario_results = mc_simulator.scenario_analysis(
                        weights, scenarios_to_run)
                    st.session_state.scenario_results = scenario_results
                    st.success("✅ Stress tests completed!")
                except Exception as e:
                    st.error(f"❌ Stress tests failed: {str(e)}")

    # Display simulation results
    if 'mc_results' in st.session_state:
        mc_results = st.session_state.mc_results
        risk_metrics = st.session_state.mc_risk_metrics

        # Price path simulation chart
        st.subheader("📈 Simulated Portfolio Paths")

        price_paths = mc_results['price_paths']
        days = list(range(price_paths.shape[1]))

        fig = go.Figure()

        # Add sample paths
        for i in range(min(num_paths_display, price_paths.shape[0])):
            fig.add_trace(go.Scatter(
                x=days,
                y=price_paths[i],
                mode='lines',
                line=dict(width=0.5, color='lightblue'),
                showlegend=False,
                opacity=0.3
            ))

        # Add percentiles
        percentiles = [5, 25, 50, 75, 95]
        colors = ['red', 'orange', 'green', 'orange', 'red']

        for p, color in zip(percentiles, colors):
            path_percentile = np.percentile(price_paths, p, axis=0)
            fig.add_trace(go.Scatter(
                x=days,
                y=path_percentile,
                mode='lines',
                name=f'{p}th Percentile',
                line=dict(width=2, color=color)
            ))

        fig.update_layout(
            title=f"Monte Carlo Portfolio Simulation ({mc_simulator.num_simulations:,} paths)",
            xaxis_title="Days",
            yaxis_title="Portfolio Value ($)",
            height=500,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Simulation summary metrics
        st.subheader("📊 Simulation Results Summary")

        summary = risk_metrics['summary']

        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

        with metrics_col1:
            st.metric(
                "Expected Final Value",
                f"${summary['expected_final_value']:,.0f}",
                f"{summary['expected_return']:+.2%}"
            )

        with metrics_col2:
            st.metric(
                "Probability of Loss",
                f"{summary['probability_of_loss']:.1%}",
                help="Probability of losing money"
            )

        with metrics_col3:
            st.metric(
                "Worst Case Scenario",
                f"${summary['max_loss']['value']:,.0f}",
                f"{summary['max_loss']['return']:+.2%}"
            )

        with metrics_col4:
            st.metric(
                "Best Case Scenario",
                f"${summary['max_gain']['value']:,.0f}",
                f"{summary['max_gain']['return']:+.2%}"
            )

        # VaR and ES metrics
        var_es_col1, var_es_col2 = st.columns(2)

        with var_es_col1:
            st.subheader("📉 Value at Risk (VaR)")
            var_data = []
            for conf_level in [90, 95, 99]:
                var_key = f'VaR_{conf_level}%'
                if var_key in risk_metrics:
                    var_data.append({
                        'Confidence Level': f"{conf_level}%",
                        'VaR Value': f"${risk_metrics[var_key]['value']:,.0f}",
                        'VaR Return': f"{risk_metrics[var_key]['return']:.2%}",
                        'Potential Loss': f"${risk_metrics[var_key]['loss_from_initial']:,.0f}"
                    })

            if var_data:
                st.dataframe(pd.DataFrame(var_data),
                             hide_index=True, use_container_width=True)

        with var_es_col2:
            st.subheader("💀 Expected Shortfall (ES)")
            es_data = []
            for conf_level in [90, 95, 99]:
                es_key = f'ES_{conf_level}%'
                if es_key in risk_metrics:
                    es_data.append({
                        'Confidence Level': f"{conf_level}%",
                        'ES Value': f"${risk_metrics[es_key]['value']:,.0f}",
                        'ES Return': f"{risk_metrics[es_key]['return']:.2%}",
                        'Expected Loss': f"${risk_metrics[es_key]['loss_from_initial']:,.0f}"
                    })

            if es_data:
                st.dataframe(pd.DataFrame(es_data),
                             hide_index=True, use_container_width=True)

    # Display stress test results
    if 'scenario_results' in st.session_state:
        st.subheader("🧪 Stress Test Results")

        scenario_results = st.session_state.scenario_results

        try:
            # Create comparison chart
            scenarios = list(scenario_results.keys())
            expected_returns = [scenario_results[s]
                                ['expected_return'] for s in scenarios]
            volatilities = [scenario_results[s]['volatility']
                            for s in scenarios]
            var_95_values = [scenario_results[s]['var_95'] for s in scenarios]

            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Expected Returns', 'Volatility',
                                'VaR 95%', 'Sharpe Ratios'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )

            # Expected returns
            fig.add_trace(
                go.Bar(x=scenarios, y=expected_returns, name='Expected Return',
                       marker_color='lightblue'),
                row=1, col=1
            )

            # Volatility
            fig.add_trace(
                go.Bar(x=scenarios, y=volatilities, name='Volatility',
                       marker_color='lightcoral'),
                row=1, col=2
            )

            # VaR 95%
            fig.add_trace(
                go.Bar(x=scenarios, y=var_95_values, name='VaR 95%',
                       marker_color='red'),
                row=2, col=1
            )

            # Sharpe ratios
            sharpe_ratios = [scenario_results[s]['sharpe_ratio']
                             for s in scenarios]
            fig.add_trace(
                go.Bar(x=scenarios, y=sharpe_ratios, name='Sharpe Ratio',
                       marker_color='green'),
                row=2, col=2
            )

            fig.update_layout(height=600, showlegend=False,
                              title="Stress Test Scenario Comparison")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying stress test results: {str(e)}")


def reports_export_tab():
    st.header("📋 Professional Reports & Export")

    if 'current_portfolio' not in st.session_state:
        st.warning(
            "⚠️ Please optimize a portfolio first in the Portfolio Builder tab")
        return

    # Report generation options
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Report Configuration")

        report_sections = st.multiselect(
            "Select Report Sections:",
            [
                "Executive Summary",
                "Portfolio Allocation",
                "Risk Metrics",
                "Performance Analysis",
                "Monte Carlo Results",
                "Stress Test Analysis",
                "Appendix"
            ],
            default=["Executive Summary",
                     "Portfolio Allocation", "Risk Metrics"]
        )

        report_format = st.selectbox(
            "Report Format:",
            ["PDF", "Excel", "CSV Data", "JSON"]
        )

        include_charts = st.checkbox("Include Charts", value=True)

    with col2:
        st.subheader("🎯 Quick Actions")

        if st.button("📄 Generate Report", type="primary"):
            generate_report(report_sections, report_format, include_charts)

        if st.button("📧 Email Report"):
            st.info("Email functionality would be implemented here")

        if st.button("☁️ Save to Cloud"):
            st.info("Cloud save functionality would be implemented here")

    # Portfolio summary for export
    st.subheader("📈 Portfolio Performance Summary")

    portfolio_data = st.session_state.portfolio_data
    current_portfolio = st.session_state.current_portfolio
    weights = current_portfolio['weights']
    tickers = portfolio_data['tickers']

    # Create summary table
    portfolio_summary = pd.DataFrame({
        'Asset': tickers,
        'Weight': [f"{w:.2%}" for w in weights],
        'Initial Value': [f"${portfolio_data['portfolio_value'] * w:,.0f}" for w in weights],
    })

    st.table(portfolio_summary)

    # Performance metrics
    st.subheader("Key Performance Metrics")

    col1, col2 = st.columns(2)

    with col1:
        metrics_data = [
            ["Expected Return",
                f"{current_portfolio['return']:.2%}", "Annualized expected return"],
            ["Portfolio Volatility",
                f"{current_portfolio['volatility']:.2%}", "Annualized standard deviation"],
            ["Sharpe Ratio", f"{current_portfolio['sharpe_ratio']:.3f}",
                "Risk-adjusted return metric"],
            ["Portfolio Value",
                f"${portfolio_data['portfolio_value']:,.0f}", "Total portfolio value"]
        ]

        metrics_df = pd.DataFrame(metrics_data, columns=[
                                  "Metric", "Value", "Description"])
        st.table(metrics_df)

    with col2:
        # Basic risk statistics
        if st.session_state.risk_calculator is not None:
            try:
                risk_calculator = st.session_state.risk_calculator
                var_metrics = risk_calculator.value_at_risk(weights)

                risk_data = [
                    ["VaR (95%, 1D)",
                     f"${-var_metrics['VaR_1D'] * portfolio_data['portfolio_value']:,.0f}", "Daily Value at Risk"],
                    ["VaR (95%, 1M)", f"${-var_metrics['VaR_1M'] * portfolio_data['portfolio_value']:,.0f}",
                     "Monthly Value at Risk"],
                    ["Expected Shortfall",
                        f"${-risk_calculator.expected_shortfall(weights)['ES_1D'] * portfolio_data['portfolio_value']:,.0f}", "Average of worst case losses"],
                    ["Max Drawdown", "See Risk Dashboard",
                        "Maximum historical decline"]
                ]

                risk_df = pd.DataFrame(risk_data, columns=[
                                       "Risk Metric", "Value", "Description"])
                st.table(risk_df)
            except Exception as e:
                st.error(f"Error displaying risk metrics: {str(e)}")

    # Asset allocation for export
    st.subheader("🎯 Asset Allocation Details")

    weights = current_portfolio['weights']
    tickers = portfolio_data['tickers']

    allocation_export = pd.DataFrame({
        'Asset': tickers,
        'Weight': weights,
        'Weight_Percent': [f"{w:.2%}" for w in weights],
        'Value_USD': [portfolio_data['portfolio_value'] * w for w in weights],
        'Value_Formatted': [f"${portfolio_data['portfolio_value'] * w:,.0f}" for w in weights]
    })

    st.dataframe(allocation_export, hide_index=True, use_container_width=True)

    # Download buttons for data
    st.subheader("💾 Download Data")

    download_col1, download_col2, download_col3 = st.columns(3)

    with download_col1:
        # Portfolio allocation CSV
        csv_data = allocation_export.to_csv(index=False)
        st.download_button(
            label="📊 Download Allocation CSV",
            data=csv_data,
            file_name=f"portfolio_allocation_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with download_col2:
        # Risk metrics JSON
        if 'mc_risk_metrics' in st.session_state:
            import json
            risk_data = st.session_state.mc_risk_metrics
            json_data = json.dumps(risk_data, indent=2, default=str)
            st.download_button(
                label="⚠️ Download Risk Metrics JSON",
                data=json_data,
                file_name=f"risk_metrics_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

    with download_col3:
        # Price data CSV
        if 'returns' in portfolio_data:
            price_csv = portfolio_data['returns'].to_csv()
            st.download_button(
                label="📈 Download Price Data CSV",
                data=price_csv,
                file_name=f"price_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


def generate_report(sections, format_type, include_charts):
    """Generate comprehensive portfolio report"""
    with st.spinner(f"Generating {format_type} report..."):
        try:
            # This would contain the actual report generation logic
            # For demo purposes, we'll show a success message
            report_content = f"""
            Portfolio Risk Analytics Report
            Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            
            Sections included: {', '.join(sections)}
            Format: {format_type}
            Charts included: {include_charts}
            
            [Report content would be generated here]
            """

            st.success("✅ Report generated successfully!")
            st.text_area("Report Preview:", report_content, height=200)

        except Exception as e:
            st.error(f"❌ Report generation failed: {str(e)}")


def create_sample_chart():
    """Create sample chart for landing page"""
    st.subheader("📊 Sample Portfolio Performance")

    if not PLOTLY_AVAILABLE:
        st.info("📈 Interactive charts will be available once plotly is installed")
        return

    try:
        # Generate sample data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.0008, 0.02, len(dates))
        portfolio_value = 100000 * (1 + returns).cumprod()

        # Create chart
        fig = go.Figure()

        # Add main portfolio value trace
        fig.add_trace(go.Scatter(
            x=dates,
            y=portfolio_value,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))

        # Add annotations for key events
        fig.add_annotation(
            x=dates[120],
            y=portfolio_value[120] * 1.05,
            text="Market Rally",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#2ca02c",
            arrowsize=1,
            arrowwidth=2
        )

        fig.add_annotation(
            x=dates[250],
            y=portfolio_value[250] * 0.95,
            text="Market Correction",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#d62728",
            arrowsize=1,
            arrowwidth=2
        )

        # Update layout
        fig.update_layout(
            title="Sample Portfolio Performance Simulation",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            height=500,
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Add sample metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Return", "15.2%", "2.3%")

        with col2:
            st.metric("Annual Volatility", "18.5%", "-1.2%")

        with col3:
            st.metric("Sharpe Ratio", "0.82", "0.15")

        with col4:
            st.metric("Max Drawdown", "-12.4%", "3.1%")

    except Exception as e:
        st.info(f"Sample chart unavailable: {str(e)}")


def check_data_availability():
    """Check if we can fetch market data"""
    if not YFINANCE_AVAILABLE:
        st.sidebar.error(
            "⚠️ yfinance not available - market data fetching disabled")
        return False

    try:
        # Quick test to see if we can fetch data
        test_data = yf.download("AAPL", period="5d", progress=False)
        if test_data.empty:
            st.sidebar.warning(
                "⚠️ Unable to fetch market data - check internet connection")
            return False
        return True
    except Exception as e:
        st.sidebar.warning(
            f"⚠️ Unable to fetch market data: {str(e)}")
        return False


if __name__ == "__main__":
    main()
