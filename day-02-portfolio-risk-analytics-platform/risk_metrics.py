import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Fallback imports for scipy
try:
    from scipy import stats
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    print("Warning: scipy not available, some risk metrics may be limited")
    SCIPY_AVAILABLE = False
    stats = None


class RiskMetrics:
    """
    Comprehensive risk metrics calculation for portfolio analysis
    """

    def __init__(self, returns: pd.DataFrame, risk_free_rate: float = 0.02):
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.portfolio_returns = None

    def set_portfolio_returns(self, weights: np.ndarray) -> pd.Series:
        """Calculate portfolio returns given weights"""
        self.portfolio_returns = (self.returns * weights).sum(axis=1)
        return self.portfolio_returns

    def value_at_risk(self, weights: np.ndarray, confidence_level: float = 0.95,
                      method: str = 'parametric') -> Dict:
        """
        Calculate Value at Risk (VaR) using different methods

        Methods:
        - parametric: Assumes normal distribution
        - historical: Uses historical percentiles
        - monte_carlo: Monte Carlo simulation
        """
        portfolio_returns = self.set_portfolio_returns(weights)

        if method == 'parametric':
            # Parametric VaR (normal distribution assumption)
            mean_return = portfolio_returns.mean()
            std_return = portfolio_returns.std()

            if SCIPY_AVAILABLE and stats:
                var_1d = stats.norm.ppf(
                    1 - confidence_level, mean_return, std_return)
            else:
                # Fallback calculation without scipy
                # Approximate normal quantile for common confidence levels
                z_scores = {0.90: -1.282, 0.95: -1.645, 0.99: -2.326}
                z_score = z_scores.get(confidence_level, -1.645)
                var_1d = mean_return + z_score * std_return

        elif method == 'historical':
            # Historical VaR
            var_1d = np.percentile(
                portfolio_returns, (1 - confidence_level) * 100)

        elif method == 'monte_carlo':
            # Monte Carlo VaR
            mean_return = portfolio_returns.mean()
            std_return = portfolio_returns.std()
            simulations = np.random.normal(mean_return, std_return, 10000)
            var_1d = np.percentile(simulations, (1 - confidence_level) * 100)

        else:
            raise ValueError(
                "Method must be 'parametric', 'historical', or 'monte_carlo'")

        # Scale to different time horizons
        var_1w = var_1d * np.sqrt(7)
        var_1m = var_1d * np.sqrt(30)
        var_1y = var_1d * np.sqrt(252)

        return {
            'VaR_1D': var_1d,
            'VaR_1W': var_1w,
            'VaR_1M': var_1m,
            'VaR_1Y': var_1y,
            'confidence_level': confidence_level,
            'method': method
        }

    def expected_shortfall(self, weights: np.ndarray, confidence_level: float = 0.95) -> Dict:
        """
        Calculate Expected Shortfall (Conditional VaR)
        Average loss beyond VaR threshold
        """
        portfolio_returns = self.set_portfolio_returns(weights)
        var_threshold = np.percentile(
            portfolio_returns, (1 - confidence_level) * 100)

        # Calculate expected shortfall
        tail_losses = portfolio_returns[portfolio_returns <= var_threshold]
        es_1d = tail_losses.mean() if len(tail_losses) > 0 else var_threshold

        # Scale to different time horizons
        es_1w = es_1d * np.sqrt(7)
        es_1m = es_1d * np.sqrt(30)
        es_1y = es_1d * np.sqrt(252)

        return {
            'ES_1D': es_1d,
            'ES_1W': es_1w,
            'ES_1M': es_1m,
            'ES_1Y': es_1y,
            'confidence_level': confidence_level
        }

    def calculate_beta(self, weights: np.ndarray, market_returns: pd.Series) -> float:
        """Calculate portfolio beta relative to market"""
        portfolio_returns = self.set_portfolio_returns(weights)

        # Align dates
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'market': market_returns
        }).dropna()

        if len(aligned_data) < 30:
            return np.nan

        covariance = np.cov(
            aligned_data['portfolio'], aligned_data['market'])[0, 1]
        market_variance = np.var(aligned_data['market'])

        return covariance / market_variance if market_variance != 0 else np.nan

    def sharpe_ratio(self, weights: np.ndarray) -> float:
        """Calculate Sharpe ratio"""
        portfolio_returns = self.set_portfolio_returns(weights)
        excess_returns = portfolio_returns.mean() * 252 - self.risk_free_rate
        volatility = portfolio_returns.std() * np.sqrt(252)

        return excess_returns / volatility if volatility != 0 else 0

    def sortino_ratio(self, weights: np.ndarray) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        portfolio_returns = self.set_portfolio_returns(weights)
        excess_returns = portfolio_returns.mean() * 252 - self.risk_free_rate

        # Downside deviation
        negative_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = negative_returns.std(
        ) * np.sqrt(252) if len(negative_returns) > 0 else 0.0001

        return excess_returns / downside_deviation if downside_deviation != 0 else 0

    def treynor_ratio(self, weights: np.ndarray, market_returns: pd.Series) -> float:
        """Calculate Treynor ratio (excess return / beta)"""
        portfolio_returns = self.set_portfolio_returns(weights)
        excess_returns = portfolio_returns.mean() * 252 - self.risk_free_rate

        beta = self.calculate_beta(weights, market_returns)

        return excess_returns / beta if beta != 0 else 0

    def information_ratio(self, weights: np.ndarray, benchmark_returns: pd.Series) -> float:
        """Calculate Information ratio (active return / tracking error)"""
        portfolio_returns = self.set_portfolio_returns(weights)

        # Align dates
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()

        if len(aligned_data) < 30:
            return 0

        active_returns = aligned_data['portfolio'] - aligned_data['benchmark']

        active_return = active_returns.mean() * 252
        tracking_error = active_returns.std() * np.sqrt(252)

        return active_return / tracking_error if tracking_error != 0 else 0

    def maximum_drawdown(self, weights: np.ndarray) -> Dict:
        """Calculate maximum drawdown and drawdown duration"""
        portfolio_returns = self.set_portfolio_returns(weights)

        # Cumulative returns
        wealth_index = (1 + portfolio_returns).cumprod()

        # Calculate running maximum
        running_max = wealth_index.cummax()

        # Calculate drawdown
        drawdown = (wealth_index / running_max - 1) * 100

        # Maximum drawdown
        max_drawdown = drawdown.min()
        max_drawdown_date = drawdown.idxmin()

        # Find the peak before the max drawdown
        peak_date = running_max.loc[:max_drawdown_date].idxmax()

        # Find the recovery date (if any)
        dates_after = running_max.loc[max_drawdown_date:] >= running_max.loc[peak_date]
        recovery_date = dates_after.idxmax() if dates_after.any() else None

        # Calculate drawdown duration
        if recovery_date is not None:
            drawdown_duration = (recovery_date - peak_date).days
            recovery_duration = (recovery_date - max_drawdown_date).days
        else:
            drawdown_duration = (drawdown.index[-1] - peak_date).days
            recovery_duration = None

        return {
            'max_drawdown_percent': max_drawdown,
            'peak_date': peak_date,
            'trough_date': max_drawdown_date,
            'recovery_date': recovery_date,
            'drawdown_duration_days': drawdown_duration,
            'recovery_duration_days': recovery_duration,
            'drawdown_series': drawdown
        }

    def correlation_analysis(self) -> pd.DataFrame:
        """Calculate correlation matrix between assets"""
        return self.returns.corr()

    def volatility_decomposition(self, weights: np.ndarray) -> pd.DataFrame:
        """Decompose portfolio volatility by asset contribution"""
        cov_matrix = self.returns.cov() * 252  # Annualized
        weights = np.array(weights)

        # Portfolio volatility
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        # Marginal contribution to risk
        mcr = np.dot(cov_matrix, weights) / portfolio_vol

        # Component contribution to risk
        ccr = weights * mcr

        # Percentage contribution to risk
        pcr = ccr / portfolio_vol * 100

        # Create a dataframe with asset names as a column (not just index)
        assets = self.returns.columns.tolist()
        decomposition = pd.DataFrame({
            'Asset': assets,
            'Weight': weights,
            'Risk_Contribution': ccr,
            'Risk_Contribution_Pct': pcr
        })

        return decomposition

    def stress_testing(self, weights: np.ndarray, scenarios: Dict[str, Dict]) -> Dict:
        """Perform stress testing on portfolio using historical or hypothetical scenarios"""
        portfolio_returns = self.set_portfolio_returns(weights)

        results = {}

        for scenario_name, scenario_params in scenarios.items():
            # Get scenario parameters
            return_shock = scenario_params.get('return_shock', 0)
            vol_multiplier = scenario_params.get('vol_multiplier', 1.0)

            # Apply shocks
            mean_return = portfolio_returns.mean() + return_shock
            volatility = portfolio_returns.std() * vol_multiplier

            # Calculate VaR under stress
            if SCIPY_AVAILABLE and stats:
                var_95 = stats.norm.ppf(0.05, mean_return, volatility)
                var_99 = stats.norm.ppf(0.01, mean_return, volatility)
            else:
                # Simple approximation
                var_95 = mean_return - 1.645 * volatility
                var_99 = mean_return - 2.326 * volatility

            # Simulated 1-year return
            implied_annual_return = mean_return * 252
            implied_annual_vol = volatility * np.sqrt(252)

            worst_case = mean_return - 3 * volatility
            best_case = mean_return + 3 * volatility

            results[scenario_name] = {
                'mean_daily_return': mean_return,
                'daily_volatility': volatility,
                'implied_annual_return': implied_annual_return,
                'implied_annual_volatility': implied_annual_vol,
                'var_95': var_95,
                'var_99': var_99,
                'worst_case_daily': worst_case,
                'best_case_daily': best_case,
                'scenario_parameters': scenario_params
            }

        return results

    def risk_metrics_summary(self, weights: np.ndarray,
                             market_returns: pd.Series = None,
                             benchmark_returns: pd.Series = None) -> Dict:
        """Generate comprehensive risk metrics report"""
        portfolio_returns = self.set_portfolio_returns(weights)

        # Basic metrics
        mean_daily_return = portfolio_returns.mean()
        annual_return = mean_daily_return * 252
        daily_vol = portfolio_returns.std()
        annual_vol = daily_vol * np.sqrt(252)

        # Sharpe ratio
        sharpe = self.sharpe_ratio(weights)

        # Sortino ratio
        sortino = self.sortino_ratio(weights)

        # Value at Risk
        var_metrics = self.value_at_risk(weights, confidence_level=0.95)

        # Expected shortfall
        es_metrics = self.expected_shortfall(weights, confidence_level=0.95)

        # Maximum drawdown
        drawdown_metrics = self.maximum_drawdown(weights)

        # Optional metrics that require additional data
        beta = self.calculate_beta(
            weights, market_returns) if market_returns is not None else None
        treynor = self.treynor_ratio(
            weights, market_returns) if market_returns is not None else None
        information = self.information_ratio(
            weights, benchmark_returns) if benchmark_returns is not None else None

        # Return comprehensive summary
        return {
            'return_metrics': {
                'daily_mean': mean_daily_return,
                'annual_return': annual_return,
            },
            'risk_metrics': {
                'daily_volatility': daily_vol,
                'annual_volatility': annual_vol,
                'beta': beta,
                'max_drawdown': drawdown_metrics['max_drawdown_percent'],
                'drawdown_duration': drawdown_metrics['drawdown_duration_days']
            },
            'risk_adjusted_metrics': {
                'sharpe_ratio': sharpe,
                'sortino_ratio': sortino,
                'treynor_ratio': treynor,
                'information_ratio': information
            },
            'var_metrics': var_metrics,
            'expected_shortfall': es_metrics,
            'drawdown_details': drawdown_metrics
        }
