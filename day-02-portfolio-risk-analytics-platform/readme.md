# 📊 Portfolio Risk Analytics Platform

**Day 2/15 of FinTech AI Sparks Challenge**

An enterprise-grade portfolio risk analytics platform implementing Modern Portfolio Theory, Monte Carlo simulations, and institutional-level risk metrics. Built with Python and Streamlit for real-time portfolio optimization and risk management.

![Portfolio Analytics Platform](https://img.shields.io/badge/STATUS-COMPLETED-brightgreen)
![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)

## 🖼️ Screenshots & Demo

### **📊 Portfolio Construction & Optimization**

![Portfolio Construction & Optimization](screenshot/1.Portfolio%20Construction%20%26%20Optimization.png)
_Interactive portfolio optimization with efficient frontier visualization and allocation charts_

### **⚠️ Risk Analytics Dashboard**

![Risk Analytics Dashboard](screenshot/2.Risk%20Analytics%20Dashboard.png)
_Comprehensive risk metrics with correlation analysis and volatility decomposition_

### **📈 Portfolio Monitoring & Monte Carlo Simulation**

![Portfolio Monitoring & Monte Carlo Simulation](screenshot/3.Portfolio%20Monitoring%20%26%20Monte%20Carlo%20Simulation.png)
_Monte Carlo simulation with 10,000+ scenario paths and percentile analysis_

### **🧪 Simulation Results & Stress Testing**

![Simulation Results & Stress Testing](screenshot/4.Simulation%20Results%20Summary%20and%20Stress%20Test%20Results.png)
_Detailed simulation metrics and market scenario stress testing_

### **📋 Professional Reports & Export**

![Professional Reports & Export](screenshot/5.Professional%20Reports%20%26%20Export.png)
_Professional portfolio reporting with multiple export formats_

## 🎯 Strategic Vision

This platform demonstrates advanced quantitative finance capabilities that separate senior engineers from junior ones. It implements portfolio-level complexity with institutional-grade analytics used by wealth management firms and portfolio managers daily.

## 🚀 Key Features

### 📊 Portfolio Construction

- **Modern Portfolio Theory** implementation with efficient frontier analysis
- **Black-Litterman model** with analyst views integration
- **Risk Parity optimization** for equal risk contribution
- **Multi-objective optimization** (Sharpe ratio, minimum volatility, maximum return)
- **Dynamic rebalancing** recommendations

### ⚠️ Advanced Risk Analytics

- **Value at Risk (VaR)** - Parametric, Historical, and Monte Carlo methods
- **Expected Shortfall** (Conditional VaR) calculations
- **Maximum Drawdown** analysis with recovery metrics
- **Sharpe, Sortino, Treynor ratios** for comprehensive performance measurement
- **Beta and correlation analysis** relative to market indices
- **Volatility decomposition** by asset contribution

### 🎲 Monte Carlo Simulations

- **10,000+ scenario simulations** for robust statistical analysis
- **Multi-timeframe stress testing** (1D, 1W, 1M, 1Y)
- **Market scenario analysis** (Bull/Bear markets, crashes, recovery)
- **Confidence interval predictions** with percentile analysis
- **Portfolio path visualization** with multiple scenarios

### 📈 Real-Time Monitoring

- **Live portfolio tracking** with performance attribution
- **Risk limit alerts** and threshold monitoring
- **Correlation heatmaps** for asset relationship analysis
- **Professional reporting** with export capabilities

## 💻 Technical Architecture

### Core Components

```
Portfolio Risk Analytics Platform/
├── portfolio_optimizer.py    # Modern Portfolio Theory & Black-Litterman
├── risk_metrics.py           # VaR, ES, Sharpe ratios, drawdown analysis
├── monte_carlo.py            # Monte Carlo simulations & stress testing
├── app.py                    # Original Streamlit application (template)
├── app_fixed.py              # Complete Streamlit application (use this)
├── docker-test.sh            # Docker build and run script
├── Dockerfile                # Containerization configuration
├── requirements.txt          # Python dependencies
├── TROUBLESHOOTING.md        # Common issues and solutions
└── README.md                 # This file
```

### Technology Stack

- **Python 3.11+** - Core language
- **Streamlit** - Interactive web application framework
- **NumPy/Pandas** - Data manipulation and numerical computing
- **SciPy** - Optimization algorithms and statistical functions
- **CVXPY** - Convex optimization for risk parity
- **Plotly** - Interactive financial charts and visualizations
- **yFinance** - Real-time market data integration

### Data Sources

- **Yahoo Finance** - Historical price and volume data
- **Risk-free rates** - Treasury bond yields
- **Market indices** - Benchmarking (S&P 500, etc.)
- **User inputs** - Portfolio preferences and constraints

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git for version control
- Internet connection for market data
- Docker (optional, for containerized deployment)

### Installation & Launch

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/fintech-ai-sparks.git
cd fintech-ai-sparks/day-02-portfolio-risk-analytics-platform
```

2. **Manual Installation:**

```bash
# Install required dependencies
pip install -r requirements.txt

# Run the application
streamlit run app_fixed.py
```

3. **Docker Deployment (Recommended):**

```bash
# Make the test script executable
chmod +x docker-test.sh

# Build and run with the provided script
./docker-test.sh
```

This script will:

- Build the Docker image with all dependencies
- Run the container with proper port mapping
- Make the application accessible at http://localhost:8501

4. **Access the platform:**
   - Open your browser to `http://localhost:8501`
   - Configure your portfolio in the sidebar:
     - Choose between real market data or demo mode
     - Select from predefined portfolios or enter custom tickers
     - Set time periods and risk parameters
   - Optimize your portfolio with different strategies
   - Analyze risk metrics and run Monte Carlo simulations
   - Export reports and visualizations

### Implementation Status

The platform is now fully implemented with all key features working:

- ✅ Portfolio optimization strategies (Max Sharpe, Min Volatility, Risk Parity)
- ✅ Risk metrics calculation (VaR, ES, Maximum Drawdown)
- ✅ Monte Carlo simulations and stress testing
- ✅ Interactive visualizations and reporting
- ✅ Docker containerization for easy deployment

### Troubleshooting

If you encounter issues, please refer to the detailed [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) file in this repository. Common issues include:

1. **"Expected 'Adj Close' column not found in data" Error:**

   - Yahoo Finance API sometimes changes its response structure
   - The app has robust error handling for this
   - Try using demo mode if market data retrieval fails

2. **Module Import Issues:**

   - Ensure all dependencies are installed with `pip install -r requirements.txt`
   - Check that all Python files are in the correct directory

3. **Docker-specific Issues:**

   - Make sure `app_fixed.py` is being used (check Dockerfile)
   - Verify that Docker is installed and running
   - Ensure port 8501 is not already in use

4. **Data Retrieval Problems:**

```bash
python --version  # Should be 3.8+
```

2. **Install dependencies manually:**

```bash
pip install streamlit pandas numpy plotly yfinance scipy scikit-learn matplotlib seaborn
```

3. **Test platform functionality:**

```bash
python test_platform.py
```

4. **Common issues:**
   - **ImportError**: Run `pip install -r requirements.txt`
   - **Port conflict**: Use `streamlit run app.py --server.port 8502`
   - **Data fetch errors**: Check internet connection
   - **Memory issues**: Reduce Monte Carlo simulations count

### Verified System Requirements

**Operating Systems:**

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Ubuntu 18.04+

**Python Versions:**

- ✅ Python 3.8
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11

## 📊 Usage Guide

### 1. Portfolio Configuration

**Asset Selection:**

- Choose from predefined portfolios (Tech Growth, Balanced Mix, Dividend Focus, etc.)
- Or create custom portfolios with your own tickers
- Select historical data period (6 months to 5 years)
- Set risk-free rate and portfolio value

### 2. Portfolio Optimization

**Optimization Strategies:**

- **Maximum Sharpe Ratio** - Best risk-adjusted returns
- **Minimum Volatility** - Lowest risk for given constraints
- **Risk Parity** - Equal risk contribution from each asset
- **Black-Litterman** - Market equilibrium with analyst views
- **Equal Weights** - Simple diversification baseline

**Constraints:**

- Maximum/minimum asset weights
- Sector exposure limits
- Investment universe restrictions

### 3. Risk Analysis

**Key Metrics Monitored:**

- Daily/Weekly/Monthly/Annual VaR at 90%, 95%, 99% confidence levels
- Expected Shortfall for tail risk assessment
- Maximum drawdown and recovery analysis
- Risk-adjusted performance ratios
- Asset correlation and concentration risk

### 4. Monte Carlo Simulation

**Simulation Parameters:**

- Time horizons: 30 days to 2 years
- Number of simulations: Up to 10,000 scenarios
- Stress test scenarios: Market crashes, recessions, high volatility
- Confidence intervals and percentile analysis

### 5. Professional Reporting

**Export Options:**

- PDF reports with executive summaries
- Excel spreadsheets with detailed metrics
- CSV data files for further analysis
- JSON format for API integration

## 🎯 Sample Portfolios

### Tech Growth Portfolio

```
AAPL (Apple) - 25%
MSFT (Microsoft) - 25%
GOOGL (Google) - 20%
AMZN (Amazon) - 20%
TSLA (Tesla) - 10%
```

### Balanced Investment Portfolio

```
SPY (S&P 500 ETF) - 40%
BND (Bond ETF) - 30%
VTI (Total Stock Market) - 20%
VXUS (International Stocks) - 10%
```

### ESG Focused Portfolio

```
ICLN (Clean Energy ETF) - 30%
ESG (ESG ETF) - 25%
ESGU (ESG US ETF) - 25%
VSGX (ESG International) - 20%
```

## 📈 Key Performance Indicators

### Risk Metrics Benchmarks

| Metric           | Excellent | Good    | Acceptable | Poor |
| ---------------- | --------- | ------- | ---------- | ---- |
| Sharpe Ratio     | >1.5      | 1.0-1.5 | 0.5-1.0    | <0.5 |
| Maximum Drawdown | <10%      | 10-20%  | 20-30%     | >30% |
| VaR (95%, Daily) | <2%       | 2-3%    | 3-5%       | >5%  |
| Sortino Ratio    | >2.0      | 1.5-2.0 | 1.0-1.5    | <1.0 |

### Portfolio Optimization Results

**Expected Outcomes:**

- Portfolio optimization completing within 30 seconds
- Efficient frontier generation with 50+ portfolios
- Monte Carlo simulation (10,000 scenarios) under 60 seconds
- Risk metrics calculation in real-time

## 🔥 Advanced Features

### 1. Black-Litterman Implementation

```python
# Incorporate analyst views
views = {
    'AAPL': 0.15,  # Expected 15% return
    'TSLA': 0.20   # Expected 20% return
}

# Optimize with market equilibrium + views
bl_portfolio = optimizer.black_litterman_optimization(
    market_caps=market_caps,
    views=views,
    view_confidence=0.25
)
```

### 2. Risk Parity Optimization

```python
# Equal risk contribution from each asset
risk_parity_portfolio = optimizer.risk_parity_optimization()
```

### 3. Stress Testing Scenarios

```python
# Predefined market scenarios
scenarios = {
    'market_crash': {'mean_shock': -0.005, 'vol_multiplier': 3.0},
    'recession': {'mean_shock': -0.002, 'vol_multiplier': 1.5},
    'high_volatility': {'vol_multiplier': 2.0}
}
```

## 📊 Competitive Advantages

### vs. Bloomberg Terminal

- ✅ **Cost-effective** - Free vs $2,000/month
- ✅ **Customizable** - Open source flexibility
- ✅ **Modern UI** - Streamlit-based interface
- ❌ Limited data sources compared to Bloomberg

### vs. Morningstar Direct

- ✅ **Real-time optimization** - Not batch processing
- ✅ **Monte Carlo integration** - Built-in simulations
- ✅ **Open architecture** - Extensible codebase
- ❌ Less comprehensive fundamental analysis

### vs. Robo-Advisors

- ✅ **Institutional-grade models** - Professional algorithms
- ✅ **Transparency** - Full algorithm visibility
- ✅ **Customization** - Tailored to specific needs
- ❌ Requires technical knowledge to operate

## 🧪 Testing & Validation

### Unit Tests

```bash
# Run comprehensive test suite
python -m pytest tests/ -v
```

### Performance Benchmarks

- Portfolio optimization: <30 seconds for 10 assets
- Monte Carlo simulation: <60 seconds for 10,000 scenarios
- Risk metrics calculation: <5 seconds real-time
- Efficient frontier: <45 seconds for 100 portfolios

### Data Quality Checks

- Historical data validation and cleaning
- Correlation matrix positive semi-definite verification
- Optimization constraint satisfaction
- Statistical significance testing

## 🚀 Deployment Options

### Local Development

```bash
streamlit run app.py --server.port 8501
```

### Docker Container

```bash
docker run -p 8501:8501 portfolio-risk-analytics
```

### Cloud Deployment

- **Streamlit Cloud** - Direct GitHub integration
- **Heroku** - Containerized deployment
- **AWS ECS** - Scalable container service
- **Google Cloud Run** - Serverless containers

## 📈 Future Enhancements

### Phase 2 Features

- [ ] **Real-time data feeds** - Live market integration
- [ ] **Options pricing models** - Black-Scholes implementation
- [ ] **Credit risk metrics** - Default probability models
- [ ] **ESG scoring integration** - Sustainability analytics

### Phase 3 Features

- [ ] **Machine learning predictions** - LSTM/Transformer models
- [ ] **Alternative data sources** - Sentiment, satellite data
- [ ] **Multi-asset class support** - Fixed income, commodities
- [ ] **Backtesting engine** - Historical strategy testing

### Enterprise Features

- [ ] **Multi-user support** - Role-based access control
- [ ] **API endpoints** - RESTful service integration
- [ ] **Database integration** - PostgreSQL/MongoDB
- [ ] **Compliance reporting** - Regulatory requirement support

## 📚 Educational Resources

### Portfolio Theory

- [Modern Portfolio Theory - Markowitz (1952)](https://www.jstor.org/stable/2975974)
- [Black-Litterman Model - Goldman Sachs (1990)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=334304)
- [Risk Parity - Bridgewater Associates](https://www.bridgewater.com/research-and-insights/risk-parity)

### Risk Management

- [Value at Risk - RiskMetrics (1996)](https://www.riskmetrics.com/)
- [Expected Shortfall - Acerbi & Tasche (2002)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1045322)
- [Maximum Drawdown Analysis - Magdon-Ismail et al. (2003)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=373041)

## 🤝 Contributing

We welcome contributions from the FinTech community!

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Add unit tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Anthony Zou**

- GitHub: [@Anthony-Zou](https://github.com/Anthony-Zou)
- LinkedIn: [Anthony Zou](https://linkedin.com/in/anthony-zou)
- Email: anthony.zou@example.com

## 🙏 Acknowledgments

- **Harry Markowitz** - Modern Portfolio Theory foundation
- **Fischer Black & Robert Litterman** - Black-Litterman model
- **Streamlit Team** - Amazing web app framework
- **Yahoo Finance** - Free financial data API
- **QuantLib** - Quantitative finance library inspiration

## 📊 Project Statistics

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)

---

**⭐ Star this repository if you find it helpful!**

_Part of the 15-day FinTech AI Sparks Challenge - Building production-ready financial applications with modern technology._
