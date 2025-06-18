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
                var_1d = stats.norm.ppf(1 - confidence_level, mean_return, std_return)
            else:
                # Fallback calculation without scipy
                # Approximate normal quantile for common confidence levels
                z_scores = {0.90: -1.282, 0.95: -1.645, 0.99: -2.326}
                z_score = z_scores.get(confidence_level, -1.645)
                var_1d = mean_return + z_score * std_return
            
        elif method == 'historical':
            # Historical VaR
            var_1d = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            
        elif method == 'monte_carlo':
            # Monte Carlo VaR
            mean_return = portfolio_returns.mean()
            std_return = portfolio_returns.std()
            simulations = np.random.normal(mean_return, std_return, 10000)
            var_1d = np.percentile(simulations, (1 - confidence_level) * 100)
            
        else:
            raise ValueError("Method must be 'parametric', 'historical', or 'monte_carlo'")
        
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
        var_threshold = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        
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
        
        covariance = np.cov(aligned_data['portfolio'], aligned_data['market'])[0, 1]
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
        downside_deviation = negative_returns.std() * np.sqrt(252)
        
        return excess_returns / downside_deviation if downside_deviation != 0 else 0
    
    def treynor_ratio(self, weights: np.ndarray, market_returns: pd.Series) -> float:
        """Calculate Treynor ratio"""
        portfolio_returns = self.set_portfolio_returns(weights)
        excess_returns = portfolio_returns.mean() * 252 - self.risk_free_rate
        beta = self.calculate_beta(weights, market_returns)
        
        return excess_returns / beta if beta != 0 and not np.isnan(beta) else np.nan
    
    def information_ratio(self, weights: np.ndarray, benchmark_returns: pd.Series) -> float:
        """Calculate Information ratio"""
        portfolio_returns = self.set_portfolio_returns(weights)
        
        # Align dates
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned_data) < 30:
            return np.nan
        
        active_returns = aligned_data['portfolio'] - aligned_data['benchmark']
        excess_return = active_returns.mean() * 252
        tracking_error = active_returns.std() * np.sqrt(252)
        
        return excess_return / tracking_error if tracking_error != 0 else 0
    
    def maximum_drawdown(self, weights: np.ndarray) -> Dict:
        """Calculate maximum drawdown and related metrics"""
        portfolio_returns = self.set_portfolio_returns(weights)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        max_drawdown = drawdown.min()
        max_drawdown_date = drawdown.idxmin()
        
        # Recovery analysis
        max_dd_idx = drawdown.idxmin()
        if max_dd_idx == drawdown.index[-1]:
            recovery_date = None
            recovery_days = None
        else:
            post_dd = drawdown[max_dd_idx:]
            recovery_idx = post_dd[post_dd >= -0.001].index  # Within 0.1% of peak
            recovery_date = recovery_idx[0] if len(recovery_idx) > 0 else None
            recovery_days = (recovery_date - max_dd_idx).days if recovery_date else None
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_date': max_drawdown_date,
            'recovery_date': recovery_date,
            'recovery_days': recovery_days,
            'current_drawdown': drawdown.iloc[-1]
        }
    
    def correlation_analysis(self) -> pd.DataFrame:
        """Calculate correlation matrix of assets"""
        return self.returns.corr()
    
    def volatility_decomposition(self, weights: np.ndarray) -> pd.DataFrame:
        """Decompose portfolio volatility by asset contributions"""
        cov_matrix = self.returns.cov() * 252  # Annualized
        portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_var)
        
        # Marginal contributions to risk
        marginal_risk = np.dot(cov_matrix, weights) / portfolio_vol
        
        # Component contributions to risk
        risk_contributions = weights * marginal_risk
        
        # Percentage contributions
        pct_contributions = risk_contributions / portfolio_vol
        
        decomposition = pd.DataFrame({
            'Asset': self.returns.columns,
            'Weight': weights,
            'Marginal_Risk': marginal_risk,
            'Risk_Contribution': risk_contributions,
            'Risk_Contribution_Pct': pct_contributions
        })
        
        return decomposition.round(4)
    
    def stress_testing(self, weights: np.ndarray, scenarios: Dict[str, Dict]) -> Dict:
        """
        Perform stress testing under different market scenarios
        
        scenarios format: {
        'scenario_name': {
            'asset_shocks': {'AAPL': -0.2, 'MSFT': -0.15, ...},
            'correlation_multiplier': 1.5
        }
        }
        """
        results = {}
        for scenario_name, scenario_config in scenarios.items():
            asset_shocks = scenario_config.get('asset_shocks', {})
            corr_multiplier = scenario_config.get('correlation_multiplier', 1.0)
            
            # Apply shocks to returns
            shocked_returns = self.returns.copy()
            
            # Apply asset-specific shocks
            for asset, shock in asset_shocks.items():
                if asset in shocked_returns.columns:
                    shocked_returns[asset] = shocked_returns[asset] * (1 + shock)
            
            # Apply correlation shock by adjusting covariance matrix
            shocked_cov = self.returns.cov() * corr_multiplier
            
            # Calculate shocked portfolio statistics
            portfolio_return = np.sum(shocked_returns.mean() * weights) * 252
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(shocked_cov, weights))) * np.sqrt(252)
            
            # Calculate VaR under stressed scenario
            stressed_portfolio_returns = (shocked_returns * weights).sum(axis=1)
            var_95 = np.percentile(stressed_portfolio_returns, 5)
            es_95 = stressed_portfolio_returns[stressed_portfolio_returns <= var_95].mean()
            
            # Store results
            results[scenario_name] = {
                'portfolio_return': portfolio_return,
                'portfolio_volatility': portfolio_vol,
                'sharpe_ratio': (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0,
                'var_95': var_95,
                'es_95': es_95
            }
            shocked_returns = self.returns.copy()
            for asset, shock in asset_shocks.items():
                if asset in shocked_returns.columns:
                    shocked_returns[asset] = shocked_returns[asset] + shock
            
            # Adjust correlations if specified
            if corr_multiplier != 1.0:
                corr_matrix = shocked_returns.corr()
                std_devs = shocked_returns.std()
                
                # Scale correlations
                scaled_corr = corr_matrix * corr_multiplier
                np.fill_diagonal(scaled_corr.values, 1.0)  # Keep diagonal as 1
                
                # Rebuild covariance matrix
                cov_matrix = np.outer(std_devs, std_devs) * scaled_corr
                
                # Generate new returns (simplified approach)
                mean_returns = shocked_returns.mean()
                shocked_returns = pd.DataFrame(
                    np.random.multivariate_normal(mean_returns, cov_matrix, len(shocked_returns)),
                    columns=shocked_returns.columns,
                    index=shocked_returns.index
                )
            
            # Calculate portfolio performance under stress
            stressed_portfolio_returns = (shocked_returns * weights).sum(axis=1)
            
            results[scenario_name] = {
                'portfolio_return': stressed_portfolio_returns.mean() * 252,
                'portfolio_volatility': stressed_portfolio_returns.std() * np.sqrt(252),
                'var_95': np.percentile(stressed_portfolio_returns, 5),
                'max_loss': stressed_portfolio_returns.min(),
                'sharpe_ratio': (stressed_portfolio_returns.mean() * 252 - self.risk_free_rate) / 
                              (stressed_portfolio_returns.std() * np.sqrt(252))
            }
        
        return results
    
    def risk_metrics_summary(self, weights: np.ndarray, 
                           market_returns: pd.Series = None,
                           benchmark_returns: pd.Series = None) -> Dict:
        """Comprehensive risk metrics summary"""
        portfolio_returns = self.set_portfolio_returns(weights)
        
        # Basic metrics
        annual_return = portfolio_returns.mean() * 252
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        
        metrics = {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': self.sharpe_ratio(weights),
            'sortino_ratio': self.sortino_ratio(weights),
        }
          # VaR and ES
        try:
            var_metrics = self.value_at_risk(weights, 0.95, 'historical')
            es_metrics = self.expected_shortfall(weights, 0.95)
            metrics.update(var_metrics)
            metrics.update(es_metrics)
        except Exception as e:
            print(f"Error calculating VaR/ES: {e}")
        except Exception as e:
            print(f"Warning: Could not calculate VaR/ES: {e}")
          # Drawdown
        try:
            dd_metrics = self.maximum_drawdown(weights)
            metrics.update(dd_metrics)
        except Exception as e:
            print(f"Warning: Could not calculate drawdown: {e}")
        
        # Market-relative metrics
        if market_returns is not None:
            try:
                metrics['beta'] = self.calculate_beta(weights, market_returns)
                metrics['treynor_ratio'] = self.treynor_ratio(weights, market_returns)
            except Exception as e:
                print(f"Error calculating market-relative metrics: {e}")
        
        if benchmark_returns is not None:
            try:
                metrics['information_ratio'] = self.information_ratio(weights, benchmark_returns)
                
                # Tracking error
                portfolio_returns = self.set_portfolio_returns(weights)
                aligned_data = pd.DataFrame({
                    'portfolio': portfolio_returns,
                    'benchmark': benchmark_returns
                }).dropna()
                
                if len(aligned_data) >= 30:
                    active_returns = aligned_data['portfolio'] - aligned_data['benchmark']
                    metrics['tracking_error'] = active_returns.std() * np.sqrt(252)
            except Exception as e:
                print(f"Error calculating benchmark-relative metrics: {e}")
        if market_returns is not None:
            try:
                metrics['beta'] = self.calculate_beta(weights, market_returns)
                metrics['treynor_ratio'] = self.treynor_ratio(weights, market_returns)
            except Exception as e:
                print(f"Warning: Could not calculate market metrics: {e}")
        
        if benchmark_returns is not None:
            try:
                metrics['information_ratio'] = self.information_ratio(weights, benchmark_returns)
            except Exception as e:
                print(f"Warning: Could not calculate information ratio: {e}")
        
        return metrics
