import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Import optimization libraries with fallbacks
try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    print("Warning: scipy not available, optimization will be limited")
    SCIPY_AVAILABLE = False

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    print("Warning: cvxpy not available, convex optimization will be limited")
    CVXPY_AVAILABLE = False

class PortfolioOptimizer:
    """
    Modern Portfolio Theory implementation with multiple optimization strategies
    """
    
    def __init__(self, returns: pd.DataFrame, risk_free_rate: float = 0.02):
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.n_assets = len(returns.columns)
        self.asset_names = returns.columns.tolist()
        
        # Calculate key statistics
        self.mean_returns = returns.mean() * 252  # Annualized
        self.cov_matrix = returns.cov() * 252     # Annualized
        
        # Market cap weights (equal weight as default)
        self.market_caps = np.ones(self.n_assets) / self.n_assets
    
    def portfolio_stats(self, weights: np.ndarray) -> dict:
        """Calculate portfolio statistics given weights"""
        # Portfolio return
        portfolio_return = np.sum(self.mean_returns * weights)
        
        # Portfolio volatility
        portfolio_variance = np.dot(weights.T, np.dot(self.cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return {
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio,
            'weights': weights
        }
    
    def max_sharpe_optimization(self, constraints: dict = None) -> dict:
        """Optimize for maximum Sharpe ratio"""
        if not SCIPY_AVAILABLE:
            # Fallback to equal weights
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
        
        def negative_sharpe(weights):
            stats = self.portfolio_stats(weights)
            return -stats['sharpe_ratio']
        
        # Constraints
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # Bounds (no short selling by default)
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Add custom constraints if provided
        if constraints:
            if 'max_weight' in constraints:
                max_weight = constraints['max_weight']
                bounds = tuple((0, max_weight) for _ in range(self.n_assets))
            
            if 'min_weight' in constraints:
                min_weight = constraints['min_weight']
                bounds = tuple((min_weight, bounds[i][1]) for i in range(self.n_assets))
        
        # Initial guess (equal weights)
        x0 = np.ones(self.n_assets) / self.n_assets
        
        try:
            result = minimize(
                negative_sharpe, x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={'maxiter': 1000}
            )
            
            if result.success:
                return self.portfolio_stats(result.x)
            else:
                # Fallback to equal weights if optimization fails
                weights = np.ones(self.n_assets) / self.n_assets
                return self.portfolio_stats(weights)
                
        except Exception as e:
            print(f"Optimization error: {e}")
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
    
    def min_volatility_optimization(self, constraints: dict = None) -> dict:
        """Optimize for minimum volatility"""
        if not SCIPY_AVAILABLE:
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
        
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # Constraints
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        if constraints:
            if 'max_weight' in constraints:
                max_weight = constraints['max_weight']
                bounds = tuple((0, max_weight) for _ in range(self.n_assets))
        
        x0 = np.ones(self.n_assets) / self.n_assets
        
        try:
            result = minimize(
                portfolio_volatility, x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={'maxiter': 1000}
            )
            
            if result.success:
                return self.portfolio_stats(result.x)
            else:
                weights = np.ones(self.n_assets) / self.n_assets
                return self.portfolio_stats(weights)
                
        except Exception as e:
            print(f"Optimization error: {e}")
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
    
    def risk_parity_optimization(self) -> dict:
        """Risk parity optimization - equal risk contribution from each asset"""
        if not SCIPY_AVAILABLE:
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
        
        def risk_budget_objective(weights):
            """Minimize the sum of squared differences in risk contributions"""
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            marginal_risk = np.dot(self.cov_matrix, weights) / portfolio_vol
            risk_contributions = weights * marginal_risk
            target_risk = portfolio_vol / self.n_assets  # Equal risk target
            return np.sum((risk_contributions - target_risk) ** 2)
        
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0.001, 1) for _ in range(self.n_assets))  # Small minimum to avoid division by zero
        x0 = np.ones(self.n_assets) / self.n_assets
        
        try:
            result = minimize(
                risk_budget_objective, x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            
            if result.success:
                return self.portfolio_stats(result.x)
            else:
                weights = np.ones(self.n_assets) / self.n_assets
                return self.portfolio_stats(weights)
                
        except Exception as e:
            print(f"Risk parity optimization error: {e}")
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
    
    def black_litterman_optimization(self, views: dict = None, view_confidence: float = 0.25) -> dict:
        """
        Simplified Black-Litterman model implementation
        
        Parameters:
        - views: Dict of asset views {'AAPL': 0.15, 'MSFT': 0.12} (expected returns)
        - view_confidence: Confidence in views (0-1)
        """
        try:
            # Market equilibrium returns (reverse optimization)
            risk_aversion = 3.0  # Typical value
            pi = risk_aversion * np.dot(self.cov_matrix, self.market_caps)
            
            # If no views provided, use market equilibrium
            if not views:
                mu_bl = pi
            else:
                # Create views matrix
                P = np.zeros((len(views), self.n_assets))
                Q = np.zeros(len(views))
                
                for i, (asset, view_return) in enumerate(views.items()):
                    if asset in self.asset_names:
                        asset_idx = self.asset_names.index(asset)
                        P[i, asset_idx] = 1
                        Q[i] = view_return
                
                # View uncertainty (omega)
                omega = np.diag([view_confidence] * len(views))
                
                # Black-Litterman formula
                tau = 0.025  # Uncertainty in the prior
                M1 = np.linalg.inv(tau * self.cov_matrix)
                M2 = np.dot(P.T, np.dot(np.linalg.inv(omega), P))
                M3 = np.dot(np.linalg.inv(tau * self.cov_matrix), pi)
                M4 = np.dot(P.T, np.dot(np.linalg.inv(omega), Q))
                
                mu_bl = np.dot(np.linalg.inv(M1 + M2), M3 + M4)
            
            # Optimize with Black-Litterman expected returns
            def negative_sharpe_bl(weights):
                portfolio_return = np.sum(mu_bl * weights)
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
                return -(portfolio_return - self.risk_free_rate) / portfolio_vol
            
            constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
            bounds = tuple((0, 1) for _ in range(self.n_assets))
            x0 = np.ones(self.n_assets) / self.n_assets
            
            if SCIPY_AVAILABLE:
                result = minimize(
                    negative_sharpe_bl, x0,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints,
                    options={'maxiter': 1000}
                )
                
                if result.success:
                    return self.portfolio_stats(result.x)
            
            # Fallback
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
            
        except Exception as e:
            print(f"Black-Litterman optimization error: {e}")
            weights = np.ones(self.n_assets) / self.n_assets
            return self.portfolio_stats(weights)
    
    def efficient_frontier(self, num_portfolios: int = 100) -> pd.DataFrame:
        """Generate efficient frontier portfolios"""
        if not SCIPY_AVAILABLE:
            # Return simple portfolios with different weights
            results = []
            for i in range(num_portfolios):
                weights = np.random.dirichlet(np.ones(self.n_assets))
                stats = self.portfolio_stats(weights)
                results.append({
                    'return': stats['return'],
                    'volatility': stats['volatility'],
                    'sharpe_ratio': stats['sharpe_ratio'],
                    'weights': weights
                })
            return pd.DataFrame(results)
        
        # Get min and max return bounds
        min_vol_portfolio = self.min_volatility_optimization()
        max_sharpe_portfolio = self.max_sharpe_optimization()
        
        min_ret = min_vol_portfolio['return']
        max_ret = max_sharpe_portfolio['return']
        
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        results = []
        
        for target_return in target_returns:
            try:
                # Optimize for minimum volatility given target return
                def portfolio_volatility(weights):
                    return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
                
                constraints = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': lambda x: np.sum(self.mean_returns * x) - target_return}
                ]
                bounds = tuple((0, 1) for _ in range(self.n_assets))
                x0 = np.ones(self.n_assets) / self.n_assets
                
                result = minimize(
                    portfolio_volatility, x0,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints,
                    options={'maxiter': 1000}
                )
                
                if result.success:
                    stats = self.portfolio_stats(result.x)
                    results.append({
                        'return': stats['return'],
                        'volatility': stats['volatility'],
                        'sharpe_ratio': stats['sharpe_ratio'],
                        'weights': result.x
                    })
                
            except Exception:
                continue
        
        return pd.DataFrame(results)
    
    def get_optimal_portfolios(self, constraints: dict = None) -> dict:
        """Get all optimal portfolio strategies"""
        portfolios = {}
        
        # Maximum Sharpe Ratio
        portfolios['max_sharpe'] = self.max_sharpe_optimization(constraints)
        
        # Minimum Volatility
        portfolios['min_volatility'] = self.min_volatility_optimization(constraints)
        
        # Risk Parity
        portfolios['risk_parity'] = self.risk_parity_optimization()
        
        # Equal Weights (baseline)
        equal_weights = np.ones(self.n_assets) / self.n_assets
        portfolios['equal_weights'] = self.portfolio_stats(equal_weights)
        
        # Black-Litterman (market equilibrium)
        portfolios['black_litterman'] = self.black_litterman_optimization()
        
        return portfolios
    
    def rebalancing_analysis(self, current_weights: np.ndarray, 
                           target_weights: np.ndarray,
                           transaction_cost: float = 0.001) -> dict:
        """Analyze rebalancing requirements and costs"""
        weight_diff = target_weights - current_weights
        turnover = np.sum(np.abs(weight_diff)) / 2
        
        # Estimate transaction costs
        total_cost = turnover * transaction_cost
        
        # Rebalancing threshold analysis
        significant_changes = np.abs(weight_diff) > 0.05  # 5% threshold
        
        return {
            'weight_differences': weight_diff,
            'turnover': turnover,
            'transaction_cost': total_cost,
            'significant_changes': significant_changes,
            'assets_to_rebalance': [self.asset_names[i] for i in range(self.n_assets) 
                                  if significant_changes[i]]
        }
