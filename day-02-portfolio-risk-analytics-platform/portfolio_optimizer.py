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
        portfolio_variance = np.dot(
            weights.T, np.dot(self.cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)

        # Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / \
            portfolio_volatility

        return {
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio,
            'weights': weights
        }

    def max_sharpe_optimization(self, constraints: dict = None) -> dict:
        """Optimize for maximum Sharpe ratio"""
        if not SCIPY_AVAILABLE:
            raise ImportError("Scipy is required for optimization")

        def negative_sharpe(weights):
            portfolio_stats = self.portfolio_stats(weights)
            return -portfolio_stats['sharpe_ratio']

        # Constraints
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        # Bounds (no short selling by default)
        bounds = tuple((0, 1) for _ in range(self.n_assets))

        # Add custom constraints if provided
        if constraints:
            max_weight = constraints.get('max_weight', 1.0)
            min_weight = constraints.get('min_weight', 0.0)
            bounds = tuple((min_weight, max_weight)
                           for _ in range(self.n_assets))

        # Initial guess (equal weights)
        x0 = np.ones(self.n_assets) / self.n_assets

        try:
            result = minimize(
                negative_sharpe,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list
            )

            optimal_weights = result['x']
            return self.portfolio_stats(optimal_weights)

        except Exception as e:
            raise Exception(f"Optimization failed: {str(e)}")

    def min_volatility_optimization(self, constraints: dict = None) -> dict:
        """Optimize for minimum volatility"""
        if not SCIPY_AVAILABLE:
            raise ImportError("Scipy is required for optimization")

        def portfolio_volatility(weights):
            portfolio_stats = self.portfolio_stats(weights)
            return portfolio_stats['volatility']

        # Constraints
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(self.n_assets))

        if constraints:
            max_weight = constraints.get('max_weight', 1.0)
            min_weight = constraints.get('min_weight', 0.0)
            bounds = tuple((min_weight, max_weight)
                           for _ in range(self.n_assets))

        x0 = np.ones(self.n_assets) / self.n_assets

        try:
            result = minimize(
                portfolio_volatility,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list
            )

            optimal_weights = result['x']
            return self.portfolio_stats(optimal_weights)

        except Exception as e:
            raise Exception(f"Optimization failed: {str(e)}")

    def risk_parity_optimization(self) -> dict:
        """Risk parity optimization - equal risk contribution from each asset"""
        if not SCIPY_AVAILABLE:
            raise ImportError("Scipy is required for optimization")

        def risk_budget_objective(weights):
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            risk_contribution = weights * \
                (np.dot(self.cov_matrix, weights)) / portfolio_vol

            # Target risk budget (equal for each asset)
            target_risk = portfolio_vol / self.n_assets

            # Sum of squared error between actual and target risk contribution
            risk_budget_error = np.sum((risk_contribution - target_risk) ** 2)
            return risk_budget_error

        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        # Small minimum to avoid division by zero
        bounds = tuple((0.001, 1) for _ in range(self.n_assets))
        x0 = np.ones(self.n_assets) / self.n_assets

        try:
            result = minimize(
                risk_budget_objective,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

            optimal_weights = result['x']
            return self.portfolio_stats(optimal_weights)

        except Exception as e:
            raise Exception(f"Risk parity optimization failed: {str(e)}")

    def black_litterman_optimization(self, views: dict = None, view_confidence: float = 0.25) -> dict:
        """
        Simplified Black-Litterman model implementation

        Parameters:
        - views: Dict of asset views {'AAPL': 0.15, 'MSFT': 0.12} (expected returns)
        - view_confidence: Confidence in views (0-1)
        """
        try:
            # Use market portfolio as prior
            market_weights = self.market_caps.copy()

            # Prior expected returns (CAPM implied)
            implied_returns = self.risk_free_rate + \
                np.dot(self.cov_matrix, market_weights)

            # If no views provided, just use market equilibrium
            if views is None or len(views) == 0:
                return self.max_sharpe_optimization()

            # Convert views to expected returns vector
            view_vector = np.zeros(self.n_assets)
            pick_matrix = np.zeros((len(views), self.n_assets))
            view_returns = np.zeros(len(views))

            for i, (asset, expected_return) in enumerate(views.items()):
                if asset in self.asset_names:
                    asset_idx = self.asset_names.index(asset)
                    pick_matrix[i, asset_idx] = 1
                    view_returns[i] = expected_return

            # Confidence in views matrix (diagonal)
            omega = np.eye(len(views)) * (1 / view_confidence)

            # Posterior expected returns
            tau = 0.05  # Standard BL scaling factor
            left_term = np.linalg.inv(tau * self.cov_matrix)
            mid_term = np.dot(pick_matrix.T, np.dot(
                np.linalg.inv(omega), pick_matrix))
            right_term = np.dot(left_term, implied_returns)
            right_term += np.dot(pick_matrix.T,
                                 np.dot(np.linalg.inv(omega), view_returns))

            posterior_returns = np.dot(np.linalg.inv(
                left_term + mid_term), right_term)

            # Store the posterior expected returns
            self.mean_returns = posterior_returns / 252  # Convert back to daily

            # Optimize with the new expected returns
            return self.max_sharpe_optimization()

        except Exception as e:
            raise Exception(f"Black-Litterman optimization failed: {str(e)}")

    def efficient_frontier(self, num_portfolios: int = 100) -> pd.DataFrame:
        """Generate efficient frontier portfolios"""
        if not SCIPY_AVAILABLE:
            raise ImportError("Scipy is required for optimization")

        # Get min and max return bounds
        min_vol_portfolio = self.min_volatility_optimization()
        max_sharpe_portfolio = self.max_sharpe_optimization()

        min_ret = min_vol_portfolio['return']
        max_ret = max_sharpe_portfolio['return']

        target_returns = np.linspace(min_ret, max_ret, num_portfolios)

        results = []

        for target_return in target_returns:
            # Set up optimization for minimum volatility at target return
            def portfolio_volatility(weights):
                return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))

            # Constraints: sum of weights = 1, return = target
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.sum(
                    self.mean_returns * x) - target_return}
            ]

            bounds = tuple((0, 1) for _ in range(self.n_assets))
            x0 = np.ones(self.n_assets) / self.n_assets

            try:
                result = minimize(
                    portfolio_volatility,
                    x0,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints
                )

                optimal_weights = result['x']
                portfolio_stats = self.portfolio_stats(optimal_weights)
                results.append(portfolio_stats)
            except:
                # Skip failed optimizations
                continue

        return pd.DataFrame(results)

    def get_optimal_portfolios(self, constraints: dict = None) -> dict:
        """Get a set of optimal portfolios with different objectives"""
        max_sharpe = self.max_sharpe_optimization(constraints)
        min_vol = self.min_volatility_optimization(constraints)
        risk_parity = self.risk_parity_optimization()

        # Equal weight portfolio
        equal_weights = np.ones(self.n_assets) / self.n_assets
        equal_weight = self.portfolio_stats(equal_weights)

        return {
            'max_sharpe': max_sharpe,
            'min_volatility': min_vol,
            'risk_parity': risk_parity,
            'equal_weight': equal_weight
        }

    def rebalancing_analysis(self, current_weights: np.ndarray,
                             target_weights: np.ndarray,
                             transaction_cost: float = 0.001) -> dict:
        """Analyze portfolio rebalancing costs and benefits"""
        # Calculate trading required
        weight_differences = target_weights - current_weights
        trades_needed = np.abs(weight_differences)

        # Calculate transaction costs
        total_turnover = np.sum(trades_needed)
        total_cost = total_turnover * transaction_cost

        # Compare metrics
        current_stats = self.portfolio_stats(current_weights)
        target_stats = self.portfolio_stats(target_weights)

        # Compare key metrics
        return_difference = target_stats['return'] - current_stats['return']
        vol_difference = target_stats['volatility'] - \
            current_stats['volatility']
        sharpe_difference = target_stats['sharpe_ratio'] - \
            current_stats['sharpe_ratio']

        # Annualize cost
        cost_annualized = total_cost * 252  # Simple approximation

        # Net benefit calculation (improve return, reduce risk)
        net_benefit = return_difference - cost_annualized

        return {
            'total_turnover': total_turnover,
            'transaction_cost': total_cost,
            'return_improvement': return_difference,
            'volatility_change': vol_difference,
            'sharpe_improvement': sharpe_difference,
            'net_benefit': net_benefit,
            'trades': {
                'assets': self.asset_names,
                'weight_differences': weight_differences,
                'trades_needed': trades_needed
            }
        }
