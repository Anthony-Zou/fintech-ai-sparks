import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="FinTech Demand Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e86ab 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e86ab;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("""
<div class="main-header">
    <h1>📈 FinTech Demand Forecasting Platform</h1>
    <p>Professional-grade financial data analysis and demand prediction using real market data</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.markdown("## 🔧 Configuration")

# Data source selection
data_source = st.sidebar.selectbox(
    "📊 Data Source",
    ["Stock Market Data", "ETF Data", "Cryptocurrency", "Custom Upload"],
    help="Choose the type of financial instrument to analyze"
)

# Symbol selection based on data source
if data_source == "Stock Market Data":
    symbols = {
        "Apple Inc.": "AAPL",
        "Microsoft Corp.": "MSFT", 
        "Tesla Inc.": "TSLA",
        "Amazon.com Inc.": "AMZN",
        "Alphabet Inc.": "GOOGL",
        "NVIDIA Corp.": "NVDA",
        "JPMorgan Chase": "JPM",
        "Visa Inc.": "V",
        "PayPal Holdings": "PYPL"
    }
elif data_source == "ETF Data":
    symbols = {
        "SPDR S&P 500": "SPY",
        "Invesco QQQ": "QQQ",
        "iShares Russell 2000": "IWM",
        "Vanguard Total Stock": "VTI",
        "Financial Select Sector": "XLF"
    }
elif data_source == "Cryptocurrency":
    symbols = {
        "Bitcoin USD": "BTC-USD",
        "Ethereum USD": "ETH-USD",
        "Cardano USD": "ADA-USD",
        "Solana USD": "SOL-USD",
        "Polygon USD": "MATIC-USD"
    }
else:
    symbols = {}

if symbols:
    selected_name = st.sidebar.selectbox("🎯 Select Instrument", list(symbols.keys()))
    symbol = symbols[selected_name]
else:
    symbol = st.sidebar.text_input("📝 Enter Symbol", "AAPL")
    selected_name = symbol

# Time period selection
period_options = {
    "1 Month": "1mo",
    "3 Months": "3mo", 
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}
period_name = st.sidebar.selectbox("📅 Time Period", list(period_options.keys()), index=3)
period = period_options[period_name]

# Forecasting parameters
forecast_days = st.sidebar.slider("🔮 Forecast Days", 7, 90, 30)
confidence_level = st.sidebar.slider("📊 Confidence Level (%)", 80, 99, 95)

# Analysis type
analysis_type = st.sidebar.multiselect(
    "📈 Analysis Features",
    ["Volume Analysis", "Price Prediction", "Volatility Analysis"],
    default=["Volume Analysis", "Price Prediction"]
)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_financial_data(symbol, period):
    """Fetch real financial data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            st.error(f"❌ No data found for symbol: {symbol}")
            return None
            
        # Reset index to get date as a column
        data = data.reset_index()
        data.columns = data.columns.str.lower()
        
        # Add simple moving averages
        if len(data) > 20:
            data['sma_20'] = data['close'].rolling(window=20).mean()
            data['sma_50'] = data['close'].rolling(window=50).mean()
            
        return data
        
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return None

def calculate_financial_metrics(data):
    """Calculate key financial metrics"""
    if data is None or len(data) == 0:
        return {}
        
    current_price = data['close'].iloc[-1]
    price_change = data['close'].iloc[-1] - data['close'].iloc[-2] if len(data) > 1 else 0
    price_change_pct = (price_change / data['close'].iloc[-2] * 100) if len(data) > 1 else 0
    
    volatility = data['close'].pct_change().std() * np.sqrt(252) * 100  # Annualized volatility
    avg_volume = data['volume'].mean()
    volume_trend = data['volume'].iloc[-5:].mean() / data['volume'].iloc[-10:-5].mean() if len(data) >= 10 else 1
    
    return {
        "current_price": current_price,
        "price_change": price_change,
        "price_change_pct": price_change_pct,
        "volatility": volatility,
        "avg_volume": avg_volume,
        "volume_trend": volume_trend,
        "total_return": ((data['close'].iloc[-1] / data['close'].iloc[0]) - 1) * 100
    }

def advanced_forecasting_models(data, target_col, forecast_days):
    """Advanced forecasting using multiple models"""
    if len(data) < 30:
        st.warning("⚠️ Insufficient data for reliable forecasting (minimum 30 days required)")
        return None, None, None
        
    # Prepare features
    data = data.copy()
    data['day_of_week'] = data['date'].dt.dayofweek
    data['month'] = data['date'].dt.month
    data['day_of_month'] = data['date'].dt.day
    data['days_from_start'] = (data['date'] - data['date'].min()).dt.days
    
    # Rolling statistics
    data['rolling_mean_7'] = data[target_col].rolling(window=7, min_periods=1).mean()
    data['rolling_std_7'] = data[target_col].rolling(window=7, min_periods=1).std()
    data['rolling_mean_30'] = data[target_col].rolling(window=30, min_periods=1).mean()
    
    # Lag features
    data['lag_1'] = data[target_col].shift(1)
    data['lag_7'] = data[target_col].shift(7)
    
    # Remove rows with NaN values
    data = data.dropna()
    
    if len(data) < 20:
        st.warning("⚠️ Insufficient clean data after feature engineering")
        return None, None, None
    
    # Features for modeling
    feature_cols = ['days_from_start', 'day_of_week', 'month', 'day_of_month', 
                   'rolling_mean_7', 'rolling_std_7', 'rolling_mean_30', 'lag_1', 'lag_7']
    
    X = data[feature_cols].fillna(method='ffill')
    y = data[target_col]
    
    # Split data
    split_point = int(len(data) * 0.8)
    X_train, X_test = X[:split_point], X[split_point:]
    y_train, y_test = y[:split_point], y[split_point:]
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Models
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42)
    }
    
    best_model = None
    best_score = float('inf')
    model_results = {}
    
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        model_results[name] = {
            'model': model,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'predictions': y_pred
        }
        
        if mae < best_score:
            best_score = mae
            best_model = model
    
    # Generate future predictions
    last_date = data['date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                periods=forecast_days, freq='D')
    
    # Create future features (simplified approach)
    future_predictions = []
    for i, date in enumerate(future_dates):
        # Use last known values and simple trend
        last_value = data[target_col].iloc[-1] if i == 0 else future_predictions[-1]
        trend = np.mean(np.diff(data[target_col].tail(10)))
        
        # Simple prediction with trend
        pred = last_value + trend
        future_predictions.append(max(0, pred))  # Ensure non-negative
    
    future_df = pd.DataFrame({
        'date': future_dates,
        target_col: future_predictions
    })
    
    return model_results, future_df, scaler

# Main application
st.markdown("---")

# Fetch financial data
if data_source != "Custom Upload":
    st.markdown(f"## 📊 Real-Time Data: {selected_name} ({symbol})")
    
    with st.spinner(f"Fetching {selected_name} data..."):
        df = fetch_financial_data(symbol, period)
    
    if df is not None:
        # Calculate metrics
        metrics = calculate_financial_metrics(df)
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"${metrics['current_price']:.2f}", 
                     f"{metrics['price_change']:.2f} ({metrics['price_change_pct']:.1f}%)")
        
        with col2:
            st.metric("Volatility (Annualized)", f"{metrics['volatility']:.1f}%")
        
        with col3:
            st.metric("Avg Daily Volume", f"{metrics['avg_volume']:,.0f}")
        
        with col4:
            st.metric("Total Return", f"{metrics['total_return']:.1f}%")
        
        # Data overview
        st.markdown("### 📈 Price and Volume Overview")
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Price Action', 'Volume'),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Price chart
        fig.add_trace(
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="Price"
            ),
            row=1, col=1
        )
        
        # Add moving averages if available
        if 'sma_20' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['sma_20'], 
                          name="SMA 20", line=dict(color='orange', width=1)),
                row=1, col=1
            )
        
        # Volume chart
        fig.add_trace(
            go.Bar(x=df['date'], y=df['volume'], name="Volume", marker_color='lightblue'),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f"{selected_name} - Price and Volume Analysis",
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analysis sections
        if "Volume Analysis" in analysis_type:
            st.markdown("### 📊 Volume Demand Forecasting")
            
            # Volume forecasting
            model_results, volume_forecast, _ = advanced_forecasting_models(
                df, 'volume', forecast_days
            )
            
            if model_results and volume_forecast is not None:
                # Model performance comparison
                st.markdown("#### 🎯 Model Performance")
                
                perf_df = pd.DataFrame({
                    'Model': list(model_results.keys()),
                    'MAE': [model_results[m]['mae'] for m in model_results.keys()],
                    'RMSE': [model_results[m]['rmse'] for m in model_results.keys()],
                    'R²': [model_results[m]['r2'] for m in model_results.keys()]
                })
                
                st.dataframe(perf_df, use_container_width=True)
                
                # Volume forecast visualization
                fig_volume = go.Figure()
                
                # Historical volume
                fig_volume.add_trace(
                    go.Scatter(
                        x=df['date'], 
                        y=df['volume'],
                        mode='lines',
                        name='Historical Volume',
                        line=dict(color='blue')
                    )
                )
                
                # Forecast
                fig_volume.add_trace(
                    go.Scatter(
                        x=volume_forecast['date'],
                        y=volume_forecast['volume'],
                        mode='lines+markers',
                        name='Volume Forecast',
                        line=dict(color='red', dash='dash')
                    )
                )
                
                fig_volume.update_layout(
                    title="Volume Demand Forecast",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    height=400
                )
                
                st.plotly_chart(fig_volume, use_container_width=True)
                
                # Forecast summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Avg Forecast Volume", f"{volume_forecast['volume'].mean():,.0f}")
                with col2:
                    st.metric("Peak Forecast Volume", f"{volume_forecast['volume'].max():,.0f}")
                with col3:
                    trend = "📈 Increasing" if volume_forecast['volume'].iloc[-1] > volume_forecast['volume'].iloc[0] else "📉 Decreasing"
                    st.metric("Trend", trend)
        
        if "Price Prediction" in analysis_type:
            st.markdown("### 💰 Price Forecasting")
            
            # Price forecasting
            model_results, price_forecast, _ = advanced_forecasting_models(
                df, 'close', forecast_days
            )
            
            if model_results and price_forecast is not None:
                # Price forecast visualization
                fig_price = go.Figure()
                
                # Historical prices
                fig_price.add_trace(
                    go.Scatter(
                        x=df['date'], 
                        y=df['close'],
                        mode='lines',
                        name='Historical Price',
                        line=dict(color='green')
                    )
                )
                
                # Forecast
                fig_price.add_trace(
                    go.Scatter(
                        x=price_forecast['date'],
                        y=price_forecast['close'],
                        mode='lines+markers',
                        name='Price Forecast',
                        line=dict(color='orange', dash='dash')
                    )
                )
                
                fig_price.update_layout(
                    title="Price Prediction",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=400
                )
                
                st.plotly_chart(fig_price, use_container_width=True)
                
                # Price forecast summary
                current_price = df['close'].iloc[-1]
                forecast_price = price_forecast['close'].iloc[-1]
                price_change = ((forecast_price - current_price) / current_price) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"${current_price:.2f}")
                with col2:
                    st.metric("Forecast Price", f"${forecast_price:.2f}", f"{price_change:.1f}%")
                with col3:
                    st.metric("Price Range", f"${price_forecast['close'].min():.2f} - ${price_forecast['close'].max():.2f}")
        
        if "Volatility Analysis" in analysis_type:
            st.markdown("### 📈 Volatility Analysis")
            
            # Calculate rolling volatility
            df['returns'] = df['close'].pct_change()
            df['volatility_30d'] = df['returns'].rolling(window=30).std() * np.sqrt(252) * 100
            
            fig_vol = go.Figure()
            fig_vol.add_trace(
                go.Scatter(
                    x=df['date'], 
                    y=df['volatility_30d'],
                    mode='lines',
                    name='30-Day Volatility',
                    line=dict(color='purple')
                )
            )
            
            fig_vol.update_layout(
                title="30-Day Rolling Volatility",
                xaxis_title="Date",
                yaxis_title="Volatility (%)",
                height=400
            )
            
            st.plotly_chart(fig_vol, use_container_width=True)
        
        # Data table
        with st.expander("📋 Detailed Data Table"):
            st.dataframe(df.tail(20), use_container_width=True)
            
        # Download data
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"{symbol}_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Custom upload functionality
    st.markdown("## 📁 Custom Data Upload")
    
    uploaded_file = st.file_uploader(
        "Upload your financial data (CSV)",
        type="csv",
        help="CSV should contain: date, volume, close (and optionally: open, high, low)"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df['date'] = pd.to_datetime(df['date'])
            st.success("✅ Data uploaded successfully!")
            
            # Display uploaded data summary
            st.markdown("### Data Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Date Range", f"{(df['date'].max() - df['date'].min()).days} days")
            with col3:
                st.metric("Columns", len(df.columns))
            
            # Show data preview
            st.dataframe(df.head(), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            df = None
    else:
        st.info("📝 Please upload a CSV file to begin analysis")
        df = None

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📈 FinTech Demand Forecasting Platform | Powered by Yahoo Finance & Advanced ML</p>
    <p>⚠️ This is for educational purposes only. Not financial advice.</p>
</div>
""", unsafe_allow_html=True)
