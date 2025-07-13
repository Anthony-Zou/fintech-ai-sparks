"""
Cross-Border Payment Settlement Platform
Enterprise-Grade Financial Infrastructure

Real-time settlement optimization across traditional banking rails,
stablecoin bridges, and direct cryptocurrency settlement.
"""

from datetime import datetime, timedelta
import asyncio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from settlement_engine.currency_converter import CurrencyConverter
from settlement_engine.settlement_optimizer import SettlementOptimizer, UrgencyLevel, RiskTolerance, SettlementPreferences
import sys
import os
# Add parent directory to path for imports BEFORE any settlement_engine imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import settlement_engine modules

# Standard library and third-party imports


# Page configuration
st.set_page_config(
    page_title="Cross-Border Settlement Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #3b82f6;
    }
    .cost-savings {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .route-option {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .optimal-route {
        border-color: #10b981;
        background-color: #ecfdf5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'converter' not in st.session_state:
    st.session_state.converter = CurrencyConverter()
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = SettlementOptimizer()


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 Cross-Border Payment Settlement Platform</h1>
        <p>Enterprise-grade financial infrastructure for global payments</p>
        <p><strong>95% cost reduction • 99% faster settlement • Full compliance automation</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar - Platform Navigation
    st.sidebar.title("🚀 Platform Modules")

    selected_module = st.sidebar.selectbox(
        "Select Module",
        [
            "💰 Settlement Calculator",
            "📊 Market Analytics",
            "🎯 Business Intelligence",
            "📈 ROI Calculator",
            "🔍 Corridor Analysis"
        ]
    )

    if selected_module == "💰 Settlement Calculator":
        settlement_calculator()
    elif selected_module == "📊 Market Analytics":
        market_analytics()
    elif selected_module == "🎯 Business Intelligence":
        business_intelligence()
    elif selected_module == "📈 ROI Calculator":
        roi_calculator()
    elif selected_module == "🔍 Corridor Analysis":
        corridor_analysis()


def settlement_calculator():
    st.header("💰 Real-Time Settlement Calculator")
    st.markdown(
        "**Compare all settlement routes and find optimal path for your payment**")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Payment Details")

        # Currency selection
        currencies = ['USD', 'EUR', 'GBP', 'SGD', 'JPY', 'AUD', 'INR',
                      'PHP', 'MYR', 'THB', 'CNY', 'HKD', 'MXN', 'BRL', 'AED']

        from_currency = st.selectbox("From Currency", currencies, index=0)
        to_currency = st.selectbox(
            "To Currency", currencies, index=3)  # Default SGD

        amount = st.number_input(
            "Amount", min_value=100.0, max_value=10000000.0, value=10000.0, step=100.0)

        urgency = st.selectbox(
            "Settlement Urgency",
            ["instant", "same_day", "next_day", "standard", "economy"],
            index=2
        )

        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["conservative", "moderate", "aggressive"],
            index=1
        )

        compliance_required = st.checkbox(
            "Compliance Required (KYC/AML)", value=True)

        if st.button("🔍 Calculate Optimal Route", type="primary"):
            with st.spinner("Analyzing settlement routes..."):
                calculate_and_display_routes(
                    from_currency, to_currency, amount, urgency, risk_tolerance, compliance_required)

    with col2:
        st.subheader("💡 Platform Benefits")

        st.markdown("""
        **🚀 Speed Advantages:**
        - Stablecoin settlement: 5-10 minutes
        - Traditional wire: 2-3 days
        - **99% time reduction**
        
        **💸 Cost Savings:**
        - Traditional fees: 2-8% + $15-50
        - Our platform: 0.1-0.5% + $0.50-2.50
        - **Up to 95% cost reduction**
        
        **🛡️ Compliance Features:**
        - Automated KYC/AML screening
        - Real-time sanctions checking
        - Regulatory reporting automation
        - Full audit trail
        
        **🌐 Global Coverage:**
        - 20+ major currencies
        - Multiple settlement rails
        - Real-time rate optimization
        """)


def calculate_and_display_routes(from_curr, to_curr, amount, urgency, risk_tolerance, compliance_required):
    """Calculate and display settlement routes"""

    try:
        # Get all available routes
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        routes = loop.run_until_complete(
            st.session_state.converter.calculate_conversion_routes(
                from_curr, to_curr, amount)
        )

        if not routes:
            st.error("No routes available for this currency pair")
            return

        # Set up preferences
        preferences = SettlementPreferences(
            urgency=UrgencyLevel(urgency),
            risk_tolerance=RiskTolerance(risk_tolerance),
            compliance_required=compliance_required
        )

        # Optimize route selection
        optimal_result = st.session_state.optimizer.optimize_settlement_route(
            routes, preferences, amount, f"{from_curr}-{to_curr}"
        )

        # Display results
        st.success("✅ Route optimization complete!")

        # Show optimal route prominently
        st.markdown("### 🎯 Recommended Settlement Route")

        optimal_route = optimal_result.route
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Method", optimal_route.method.replace('_', ' ').title())
        with col2:
            st.metric("Total Cost", f"${optimal_route.total_cost:.2f}")
        with col3:
            st.metric("Final Amount", f"${optimal_route.final_amount:.2f}")
        with col4:
            st.metric("Settlement Time", optimal_route.estimated_time)

        # Cost savings highlight
        if optimal_result.cost_vs_alternatives:
            traditional_savings = optimal_result.cost_vs_alternatives.get(
                'traditional', 0)
            if traditional_savings > 0:
                savings_pct = (traditional_savings / amount) * 100
                st.markdown(f"""
                <div class="cost-savings">
                    <h3>💰 Cost Savings vs Traditional Banking</h3>
                    <h2>${traditional_savings:.2f} saved ({savings_pct:.1f}%)</h2>
                </div>
                """, unsafe_allow_html=True)

        # Selection rationale
        st.markdown("### 📋 Selection Rationale")
        st.info(f"**Why this route:** {optimal_result.selection_reason}")

        # All routes comparison
        st.markdown("### 📊 All Available Routes")

        routes_df = pd.DataFrame([
            {
                'Method': route.method.replace('_', ' ').title(),
                'Cost': f"${route.total_cost:.2f}",
                'Fee %': f"{route.fee_percentage:.3f}%",
                'Fixed Fee': f"${route.fixed_fee:.2f}",
                'Time': route.estimated_time,
                'Final Amount': f"${route.final_amount:.2f}",
                'Confidence': f"{route.confidence_score:.2f}"
            }
            for route in sorted(routes, key=lambda x: x.total_cost)
        ])

        st.dataframe(routes_df, use_container_width=True)

        # Visualization
        create_route_comparison_chart(routes)

    except Exception as e:
        st.error(f"Error calculating routes: {str(e)}")


def create_route_comparison_chart(routes):
    """Create cost and time comparison chart"""

    methods = [route.method.replace('_', ' ').title() for route in routes]
    costs = [route.total_cost for route in routes]
    times = [route.estimated_time for route in routes]

    fig = go.Figure()

    # Add cost bars
    fig.add_trace(go.Bar(
        name='Total Cost ($)',
        x=methods,
        y=costs,
        marker_color='#3b82f6'
    ))

    fig.update_layout(
        title="Settlement Route Cost Comparison",
        xaxis_title="Settlement Method",
        yaxis_title="Total Cost ($)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def market_analytics():
    st.header("📊 Market Analytics Dashboard")

    # Major corridors analysis
    corridors = [
        ('USD', 'SGD', 'US → Singapore'),
        ('USD', 'PHP', 'US → Philippines'),
        ('USD', 'INR', 'US → India'),
        ('AED', 'INR', 'UAE → India'),
        ('SGD', 'PHP', 'Singapore → Philippines'),
        ('USD', 'MXN', 'US → Mexico')
    ]

    st.subheader("🌍 Major Remittance Corridors")

    corridor_data = []

    for from_curr, to_curr, name in corridors:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analytics = loop.run_until_complete(
                st.session_state.converter.get_corridor_analytics(
                    from_curr, to_curr)
            )

            corridor_data.append({
                'Corridor': name,
                'Savings %': f"{analytics.get('max_savings_pct', 0):.1f}%",
                'Traditional Cost': f"${analytics.get('traditional_cost', 0):.0f}",
                'Stablecoin Cost': f"${analytics.get('stablecoin_cost', 0):.0f}",
                'Annual Savings (10M Volume)': f"${analytics.get('annual_savings_10m', 0):,.0f}"
            })
        except:
            corridor_data.append({
                'Corridor': name,
                'Savings %': 'N/A',
                'Traditional Cost': 'N/A',
                'Stablecoin Cost': 'N/A',
                'Annual Savings (10M Volume)': 'N/A'
            })

    corridors_df = pd.DataFrame(corridor_data)
    st.dataframe(corridors_df, use_container_width=True)

    # Market opportunity visualization
    st.subheader("💰 Market Opportunity Analysis")

    market_data = {
        'Singapore → Philippines': {'volume': 7, 'savings': 200},
        'UAE → India': {'volume': 15, 'savings': 400},
        'US → Mexico': {'volume': 60, 'savings': 1500},
        'US → India': {'volume': 25, 'savings': 600},
        'US → Philippines': {'volume': 12, 'savings': 300}
    }

    corridors = list(market_data.keys())
    volumes = [market_data[c]['volume'] for c in corridors]
    savings = [market_data[c]['savings'] for c in corridors]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=volumes,
        y=savings,
        mode='markers+text',
        text=corridors,
        textposition="top center",
        marker=dict(
            size=[v*2 for v in volumes],
            color=savings,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Annual Savings Potential ($M)")
        )
    ))

    fig.update_layout(
        title="Remittance Market Opportunity: Volume vs Savings Potential",
        xaxis_title="Annual Volume ($B)",
        yaxis_title="Annual Savings Potential ($M)",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def business_intelligence():
    st.header("🎯 Business Intelligence Center")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Key Performance Indicators")

        # Mock KPIs for demo
        st.metric("Total Volume Processed", "$2.4B", "+23%")
        st.metric("Average Cost Savings", "87%", "+5%")
        st.metric("Settlement Success Rate", "99.7%", "+0.2%")
        st.metric("Customer Satisfaction", "4.8/5", "+0.1")

    with col2:
        st.subheader("🎯 Business Metrics")

        st.metric("Revenue (Monthly)", "$1.2M", "+18%")
        st.metric("Active Corridors", "45", "+3")
        st.metric("Enterprise Clients", "127", "+12")
        st.metric("Compliance Score", "98.5%", "+1.2%")

    # Revenue breakdown
    st.subheader("💰 Revenue Breakdown by Service")

    revenue_data = {
        'Service': ['Transaction Fees', 'SaaS Licensing', 'White-label Solutions', 'Consulting Services'],
        'Monthly Revenue': [720000, 340000, 180000, 60000],
        'Growth Rate': ['+15%', '+25%', '+30%', '+20%']
    }

    fig = px.pie(
        values=revenue_data['Monthly Revenue'],
        names=revenue_data['Service'],
        title="Monthly Revenue Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)


def roi_calculator():
    st.header("📈 ROI Calculator for Enterprises")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Payment Profile")

        monthly_volume = st.number_input(
            "Monthly Payment Volume ($)", min_value=10000, value=1000000, step=10000)
        current_fee_pct = st.slider(
            "Current Fee Percentage", 0.5, 8.0, 3.0, 0.1) / 100
        current_fixed_fee = st.number_input(
            "Current Fixed Fee per Transaction ($)", min_value=5.0, value=25.0, step=5.0)
        transactions_per_month = st.number_input(
            "Transactions per Month", min_value=10, value=100, step=10)

        implementation_cost = st.number_input(
            "Implementation Cost ($)", min_value=10000, value=50000, step=5000)

    with col2:
        st.subheader("Projected Savings with Our Platform")

        # Calculate current costs
        current_monthly_cost = (
            monthly_volume * current_fee_pct) + (current_fixed_fee * transactions_per_month)

        # Calculate platform costs
        platform_fee_pct = 0.0015  # 0.15%
        platform_fixed_fee = 2.5
        platform_monthly_cost = (
            monthly_volume * platform_fee_pct) + (platform_fixed_fee * transactions_per_month)

        # Calculate savings
        monthly_savings = current_monthly_cost - platform_monthly_cost
        annual_savings = monthly_savings * 12
        roi_months = implementation_cost / \
            monthly_savings if monthly_savings > 0 else float('inf')

        st.metric("Current Monthly Cost", f"${current_monthly_cost:,.2f}")
        st.metric("Platform Monthly Cost", f"${platform_monthly_cost:,.2f}")
        st.metric("Monthly Savings", f"${monthly_savings:,.2f}",
                  f"{(monthly_savings/current_monthly_cost)*100:.1f}%")
        st.metric("Annual Savings", f"${annual_savings:,.2f}")
        st.metric("ROI Payback Period", f"{roi_months:.1f} months" if roi_months != float(
            'inf') else "N/A")

    # ROI Timeline
    st.subheader("📊 5-Year ROI Projection")

    years = list(range(1, 6))
    cumulative_savings = [annual_savings * year -
                          implementation_cost for year in years]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=years,
        y=cumulative_savings,
        name='Cumulative Net Savings',
        marker_color=['red' if x < 0 else 'green' for x in cumulative_savings]
    ))

    fig.update_layout(
        title="5-Year Cumulative Net Savings",
        xaxis_title="Year",
        yaxis_title="Cumulative Savings ($)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def corridor_analysis():
    st.header("🔍 Detailed Corridor Analysis")

    st.markdown(
        "**Deep dive into specific payment corridors with market intelligence**")

    # Corridor selection
    corridor_options = {
        'US → Singapore': ('USD', 'SGD'),
        'US → Philippines': ('USD', 'PHP'),
        'US → India': ('USD', 'INR'),
        'UAE → India': ('AED', 'INR'),
        'Singapore → Philippines': ('SGD', 'PHP'),
        'US → Mexico': ('USD', 'MXN')
    }

    selected_corridor = st.selectbox(
        "Select Corridor", list(corridor_options.keys()))
    from_curr, to_curr = corridor_options[selected_corridor]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📊 {selected_corridor} Analysis")

        # Market data (mock for demo)
        market_info = {
            'US → Singapore': {
                'annual_volume': '$8.5B',
                'avg_transaction': '$12,500',
                'primary_use': 'Business payments, expat remittances',
                'regulatory': 'MAS regulated, low friction'
            },
            'US → Philippines': {
                'annual_volume': '$18.2B',
                'avg_transaction': '$450',
                'primary_use': 'OFW remittances',
                'regulatory': 'BSP oversight, strict KYC'
            },
            'UAE → India': {
                'annual_volume': '$15.1B',
                'avg_transaction': '$850',
                'primary_use': 'Expat worker remittances',
                'regulatory': 'CBUAE/RBI coordination'
            }
        }

        info = market_info.get(selected_corridor, {
            'annual_volume': 'Data not available',
            'avg_transaction': 'Data not available',
            'primary_use': 'Mixed usage',
            'regulatory': 'Standard compliance'
        })

        st.metric("Annual Volume", info['annual_volume'])
        st.metric("Average Transaction", info['avg_transaction'])
        st.info(f"**Primary Use:** {info['primary_use']}")
        st.info(f"**Regulatory:** {info['regulatory']}")

    with col2:
        st.subheader("💰 Cost Comparison Analysis")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analytics = loop.run_until_complete(
                st.session_state.converter.get_corridor_analytics(
                    from_curr, to_curr)
            )

            if 'error' not in analytics:
                st.metric("Cost Savings",
                          f"{analytics.get('max_savings_pct', 0):.1f}%")
                st.metric("Traditional Cost",
                          f"${analytics.get('traditional_cost', 0):.2f}")
                st.metric("Stablecoin Cost",
                          f"${analytics.get('stablecoin_cost', 0):.2f}")
                st.metric("Annual Savings (10M Volume)",
                          f"${analytics.get('annual_savings_10m', 0):,.0f}")
            else:
                st.error("Analytics data unavailable")

        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")

    # Business recommendations
    st.subheader("🎯 Business Recommendations")

    recommendations = {
        'US → Singapore': [
            "Target B2B payments and treasury operations",
            "Focus on speed advantages for time-sensitive transactions",
            "Leverage Singapore's crypto-friendly regulatory environment"
        ],
        'US → Philippines': [
            "Partner with OFW-focused banks and remittance providers",
            "Emphasize cost savings for small-value transactions",
            "Ensure robust compliance with BSP requirements"
        ],
        'UAE → India': [
            "Target expat worker communities",
            "Integrate with popular digital wallet providers",
            "Focus on reliability and regulatory compliance"
        ]
    }

    corridor_recommendations = recommendations.get(selected_corridor, [
        "Analyze market dynamics and competition",
        "Identify key customer segments",
        "Develop regulatory compliance strategy"
    ])

    for i, rec in enumerate(corridor_recommendations, 1):
        st.success(f"**{i}.** {rec}")


if __name__ == "__main__":
    main()
