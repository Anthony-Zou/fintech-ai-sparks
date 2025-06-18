import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class MonteCarloSimulator:
    """
    Monte Carlo simulation for portfolio stress testing and scenario analysis
    """
    
    def __init__(self, returns: pd.DataFrame, num_simulations: int = 10000, risk_free_rate: float = 0.02):
        self.returns = returns
        self.num_simulations = num_simulations
        self.mean_returns = returns.mean()
        self.cov_matrix = returns.cov()
        self.risk_free_rate = risk_free_rate
        
    def generate_price_paths(self, weights: np.ndarray, time_horizon: int = 252,
                           initial_portfolio_value: float = 100000) -> Dict:
        """
        Generate Monte Carlo price paths for portfolio
        
        Parameters:
        - weights: Portfolio weights
        - time_horizon: Number of days to simulate
        - initial_portfolio_value: Starting portfolio value
        """
        # Portfolio statistics
        portfolio_mean = np.sum(self.mean_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # Generate random returns
        random_returns = np.random.normal(
            portfolio_mean, portfolio_vol, 
            (self.num_simulations, time_horizon)
        )
        
        # Calculate cumulative price paths
        price_paths = np.zeros((self.num_simulations, time_horizon + 1))
        price_paths[:, 0] = initial_portfolio_value
        
        for t in range(1, time_horizon + 1):
            price_paths[:, t] = price_paths[:, t-1] * (1 + random_returns[:, t-1])
        
        # Calculate final values and returns
        final_values = price_paths[:, -1]
        total_returns = (final_values - initial_portfolio_value) / initial_portfolio_value
        
        return {
            'price_paths': price_paths,
            'final_values': final_values,
            'total_returns': total_returns,
            'mean_final_value': np.mean(final_values),
            'std_final_value': np.std(final_values),
            'portfolio_mean_daily': portfolio_mean,
            'portfolio_vol_daily': portfolio_vol
        }
    
    def calculate_risk_metrics_mc(self, weights: np.ndarray, 
                                 confidence_levels: List[float] = [0.95, 0.99],
                                 time_horizon: int = 252,
                                 initial_value: float = 100000) -> Dict:
        """Calculate risk metrics using Monte Carlo simulation"""
        simulation_results = self.generate_price_paths(weights, time_horizon, initial_value)
        final_values = simulation_results['final_values']
        total_returns = simulation_results['total_returns']
        
        metrics = {}
        
        # Value at Risk and Expected Shortfall for different confidence levels
        for conf_level in confidence_levels:
            var_value = np.percentile(final_values, (1 - conf_level) * 100)
            var_return = np.percentile(total_returns, (1 - conf_level) * 100)
            
            # Expected Shortfall
            tail_losses_value = final_values[final_values <= var_value]
            tail_losses_return = total_returns[total_returns <= var_return]
            
            es_value = np.mean(tail_losses_value) if len(tail_losses_value) > 0 else var_value
            es_return = np.mean(tail_losses_return) if len(tail_losses_return) > 0 else var_return
            
            metrics[f'VaR_{int(conf_level*100)}%'] = {
                'value': var_value,
                'return': var_return,
                'loss_from_initial': initial_value - var_value
            }
            
            metrics[f'ES_{int(conf_level*100)}%'] = {
                'value': es_value,
                'return': es_return,
                'loss_from_initial': initial_value - es_value
            }
        
        # Probability of loss
        prob_loss = np.sum(final_values < initial_value) / self.num_simulations
        
        # Maximum loss
        max_loss_value = np.min(final_values)
        max_loss_return = np.min(total_returns)
        
        # Maximum gain
        max_gain_value = np.max(final_values)
        max_gain_return = np.max(total_returns)
        
        metrics['summary'] = {
            'probability_of_loss': prob_loss,
            'expected_final_value': np.mean(final_values),
            'expected_return': np.mean(total_returns),
            'volatility_of_returns': np.std(total_returns),
            'max_loss': {
                'value': max_loss_value,
                'return': max_loss_return,
                'loss_from_initial': initial_value - max_loss_value
            },
            'max_gain': {
                'value': max_gain_value,
                'return': max_gain_return,
                'gain_from_initial': max_gain_value - initial_value
            }
        }
        
        return metrics
    
    def stress_test_scenarios(self, weights: np.ndarray, 
                            scenarios: Dict[str, Dict],
                            time_horizon: int = 252,
                            initial_value: float = 100000) -> Dict:
        """
        Run Monte Carlo simulations under different stress scenarios
        
        scenarios format: {
            'market_crash': {
                'mean_shock': -0.002,  # Daily return shock
                'vol_multiplier': 2.0,  # Volatility multiplier
                'correlation_shock': 0.3  # Additional correlation
            }
        }
        """
        results = {}
          # Original portfolio statistics
        portfolio_mean = np.sum(self.mean_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        for scenario_name, scenario_params in scenarios.items():
            # Apply scenario shocks
            shocked_mean = portfolio_mean + scenario_params.get('mean_shock', 0)
            shocked_vol = portfolio_vol * scenario_params.get('vol_multiplier', 1.0)
            
            # Generate stressed returns
            stressed_returns = np.random.normal(
                shocked_mean, shocked_vol, 
                (self.num_simulations, time_horizon)
            )
            
            # Calculate price paths under stress scenario
            price_paths = np.zeros((self.num_simulations, time_horizon + 1))
            price_paths[:, 0] = initial_value
            
            for t in range(1, time_horizon + 1):
                price_paths[:, t] = price_paths[:, t-1] * (1 + stressed_returns[:, t-1])
            
            # Calculate final values and metrics
            final_values = price_paths[:, -1]
            total_returns = (final_values - initial_value) / initial_value
            
            # Value at Risk
            var_90 = np.percentile(final_values, 10)
            var_95 = np.percentile(final_values, 5)
            var_99 = np.percentile(final_values, 1)
            
            # Expected shortfall
            es_90 = np.mean(final_values[final_values <= var_90])
            es_95 = np.mean(final_values[final_values <= var_95])
            es_99 = np.mean(final_values[final_values <= var_99])
            
            # Store results
            results[scenario_name] = {
                'expected_return': np.mean(total_returns),
                'volatility': np.std(total_returns),
                'mean_final_value': np.mean(final_values),
                'median_final_value': np.median(final_values),
                'var_90': var_90,
                'var_95': var_95,
                'var_99': var_99,
                'es_90': es_90,
                'es_95': es_95,
                'es_99': es_99,
                'worst_case': np.min(final_values),
                'best_case': np.max(final_values),
                'probability_of_loss': np.sum(final_values < initial_value) / self.num_simulations,
                'sharpe_ratio': (np.mean(total_returns) - (self.risk_free_rate * (time_horizon / 252))) / 
                                np.std(total_returns) if np.std(total_returns) > 0 else 0
            }
            stressed_returns = np.random.normal(
                shocked_mean, shocked_vol,
                (self.num_simulations, time_horizon)
            )
            
            # Calculate price paths under stress
            stressed_paths = np.zeros((self.num_simulations, time_horizon + 1))
            stressed_paths[:, 0] = initial_value
            
            for t in range(1, time_horizon + 1):
                stressed_paths[:, t] = stressed_paths[:, t-1] * (1 + stressed_returns[:, t-1])
            
            final_values = stressed_paths[:, -1]
            total_returns = (final_values - initial_value) / initial_value
            
            # Calculate metrics for this scenario
            var_95 = np.percentile(final_values, 5)
            var_99 = np.percentile(final_values, 1)
            expected_value = np.mean(final_values)
            prob_loss = np.sum(final_values < initial_value) / self.num_simulations
            
            results[scenario_name] = {
                'expected_final_value': expected_value,
                'expected_return': np.mean(total_returns),
                'volatility': np.std(total_returns),
                'var_95': var_95,
                'var_99': var_99,
                'probability_of_loss': prob_loss,
                'worst_case': np.min(final_values),
                'best_case': np.max(final_values),
                'price_paths': stressed_paths,
                'scenario_params': scenario_params
            }
        
        return results
      def efficient_frontier_mc(self, num_portfolios: int = 1000,
                            time_horizon: int = 252) -> pd.DataFrame:
        """
        Generate efficient frontier using Monte Carlo optimization
        """
        n_assets = len(self.returns.columns)
        results = []
        
        for _ in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)  # Normalize to sum to 1
            
            # Calculate portfolio metrics using Monte Carlo
            mc_results = self.generate_price_paths(weights, time_horizon)
            
            portfolio_mean = np.sum(self.mean_returns * weights)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            
            # Annualize metrics
            expected_return = portfolio_mean * 252
            volatility = portfolio_vol * np.sqrt(252)
            sharpe_ratio = (expected_return - self.risk_free_rate) / volatility if volatility > 0 else 0
              # Add Monte Carlo metrics
            results.append({
                'return': expected_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'weights': weights,
                'mc_mean_final': mc_results['mean_final_value'],
                'mc_std_final': mc_results['std_final_value'],
                'var_95': np.percentile(mc_results['final_values'], 5),
                'max_drawdown': self._calculate_max_drawdown(mc_results['price_paths'][0])
            })
            
        return pd.DataFrame(results)
            
            # Calculate VaR using simulation
            final_returns = mc_results['total_returns']
            var_95 = np.percentile(final_returns, 5)
            
            results.append({
                'expected_return': expected_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'var_95': var_95,
                'weights': weights
            })
        
        return pd.DataFrame(results)
    
    def _calculate_max_drawdown(self, prices):
        """Helper function to calculate maximum drawdown from price series"""
        peak = np.maximum.accumulate(prices)
        drawdown = (prices - peak) / peak
        return np.min(drawdown)
        
    def portfolio_optimization_mc(self, target_return: float = None,
                                target_vol: float = None,
                                objective: str = 'sharpe') -> Dict:
        """
        Portfolio optimization using Monte Carlo approach
        
        Parameters:
        - target_return: Target annual return
        - target_vol: Target annual volatility
        - objective: 'sharpe', 'min_vol', 'max_return'
        """
        n_assets = len(self.returns.columns)
        best_portfolio = None
        best_metric = -np.inf if objective in ['sharpe', 'max_return'] else np.inf
        
        # Generate random portfolios
        for _ in range(self.num_simulations):
            # Generate random weights
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)  # Normalize to sum to 1
            
            # Calculate portfolio statistics
            portfolio_mean = np.sum(self.mean_returns * weights)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            
            # Annualize metrics
            expected_return = portfolio_mean * 252
            volatility = portfolio_vol * np.sqrt(252)
            sharpe_ratio = (expected_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            
            # Check constraints
            if target_return is not None and expected_return < target_return:
                continue
                
            if target_vol is not None and volatility > target_vol:
                continue
                
            # Evaluate based on objective
            if objective == 'sharpe':
                metric = sharpe_ratio
                is_better = metric > best_metric
            elif objective == 'min_vol':
                metric = volatility
                is_better = metric < best_metric
            elif objective == 'max_return':
                metric = expected_return
                is_better = metric > best_metric
            else:
                raise ValueError("Objective must be 'sharpe', 'min_vol', or 'max_return'")
                
            # Update if better
            if best_portfolio is None or is_better:
                best_metric = metric
                best_portfolio = {
                    'weights': weights,
                    'return': expected_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio
                }
        
        return best_portfolio
    
    def scenario_analysis(self, weights: np.ndarray,
                         market_conditions: List[str] = None) -> Dict:
        """
        Predefined scenario analysis for common market conditions
        """
        if market_conditions is None:
            market_conditions = ['bull_market', 'bear_market', 'high_volatility', 
                               'recession', 'market_crash', 'recovery']
        
        # Predefined scenarios
        scenarios = {
            'bull_market': {
                'mean_shock': 0.001,   # +0.1% daily boost
                'vol_multiplier': 0.8,  # Lower volatility
                'correlation_shock': -0.1
            },
            'bear_market': {
                'mean_shock': -0.001,  # -0.1% daily drag
                'vol_multiplier': 1.3,  # Higher volatility
                'correlation_shock': 0.2
            },
            'high_volatility': {
                'mean_shock': 0,
                'vol_multiplier': 2.0,  # Double volatility
                'correlation_shock': 0.1
            },
            'recession': {
                'mean_shock': -0.002,  # -0.2% daily
                'vol_multiplier': 1.5,
                'correlation_shock': 0.3
            },
            'market_crash': {
                'mean_shock': -0.005,  # -0.5% daily
                'vol_multiplier': 3.0,  # Triple volatility
                'correlation_shock': 0.5
            },
            'recovery': {
                'mean_shock': 0.002,   # +0.2% daily
                'vol_multiplier': 1.2,
                'correlation_shock': 0.1
            }
        }
        
        # Filter scenarios based on user selection
        selected_scenarios = {k: v for k, v in scenarios.items() 
                            if k in market_conditions}
        
        return self.stress_test_scenarios(weights, selected_scenarios)
    
    def get_simulation_summary(self, weights: np.ndarray,
                             time_horizon: int = 252,
                             initial_value: float = 100000) -> Dict:
        """Get comprehensive Monte Carlo simulation summary"""
        
        # Generate price paths
        mc_results = self.generate_price_paths(weights, time_horizon, initial_value)
        
        # Calculate risk metrics
        risk_metrics = self.calculate_risk_metrics_mc(weights, [0.90, 0.95, 0.99], 
                                                    time_horizon, initial_value)
        
        # Scenario analysis
        scenario_results = self.scenario_analysis(weights)
        
        summary = {
            'simulation_parameters': {
                'num_simulations': self.num_simulations,
                'time_horizon_days': time_horizon,
                'initial_portfolio_value': initial_value
            },
            'price_simulation': mc_results,
            'risk_metrics': risk_metrics,
            'scenario_analysis': scenario_results
        }
        
        return summary
