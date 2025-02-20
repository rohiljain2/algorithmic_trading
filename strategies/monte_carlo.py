import numpy as np
import pandas as pd
from typing import Tuple, List
from scipy.stats import norm

class MonteCarloSimulator:
    def __init__(self, n_simulations: int = 1000, n_days: int = 252):
        self.n_simulations = n_simulations
        self.n_days = n_days
        
    def simulate_prices(self, data: pd.DataFrame) -> Tuple[np.ndarray, dict]:
        """
        Simulate future stock prices using Monte Carlo simulation
        Returns simulated prices and risk metrics
        """
        # Calculate daily returns and volatility
        returns = np.log(data['Close'] / data['Close'].shift(1))
        mu = returns.mean()
        sigma = returns.std()
        
        # Generate random walks
        drift = mu - (sigma ** 2) / 2
        daily_returns = np.exp(drift + sigma * norm.rvs(size=(self.n_days, self.n_simulations)))
        
        # Simulate price paths
        last_price = data['Close'].iloc[-1]
        price_paths = np.zeros((self.n_days, self.n_simulations))
        price_paths[0] = last_price
        
        for t in range(1, self.n_days):
            price_paths[t] = price_paths[t-1] * daily_returns[t]
            
        # Calculate risk metrics
        metrics = self._calculate_risk_metrics(price_paths, last_price)
        
        return price_paths, metrics
    
    def _calculate_risk_metrics(self, price_paths: np.ndarray, current_price: float) -> dict:
        """Calculate various risk metrics from simulated paths"""
        final_prices = price_paths[-1]
        returns = (final_prices - current_price) / current_price
        
        metrics = {
            'expected_return': np.mean(returns),
            'var_95': np.percentile(returns, 5),  # 95% VaR
            'var_99': np.percentile(returns, 1),  # 99% VaR
            'upside_potential': np.mean(returns[returns > 0]),
            'downside_risk': np.mean(returns[returns < 0]),
            'prob_positive': np.mean(returns > 0),
            'max_drawdown': self._calculate_max_drawdown(price_paths)
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, price_paths: np.ndarray) -> float:
        """Calculate the average maximum drawdown across all paths"""
        drawdowns = []
        for path in price_paths.T:
            rolling_max = np.maximum.accumulate(path)
            drawdown = np.min((path - rolling_max) / rolling_max)
            drawdowns.append(drawdown)
        return np.mean(drawdowns) 