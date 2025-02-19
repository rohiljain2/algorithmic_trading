import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, data):
        self.data = data.copy()  # Make a copy to avoid modifying original data
        self.positions = None
        self.portfolio_value = None
        self.initial_capital = 100000
        
    def calculate_metrics(self):
        """Calculate trading metrics like Sharpe ratio, max drawdown, etc."""
        if self.portfolio_value is None or len(self.portfolio_value) == 0:
            return {
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_return': 0.0
            }
            
        portfolio_series = pd.Series(self.portfolio_value)
        returns = portfolio_series.pct_change().dropna()
        
        if len(returns) == 0:
            return {
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_return': 0.0
            }
        
        sharpe = self.calculate_sharpe_ratio(returns)
        max_dd = self.calculate_max_drawdown(portfolio_series)
        total_return = (portfolio_series.iloc[-1] - portfolio_series.iloc[0]) / portfolio_series.iloc[0]
        
        return {
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'total_return': total_return
        }
    
    def calculate_sharpe_ratio(self, returns):
        """Calculate the Sharpe ratio of the strategy"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        risk_free_rate = 0.02  # 2% annual risk-free rate
        excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def calculate_max_drawdown(self, portfolio_values):
        """Calculate the maximum drawdown of the strategy"""
        rolling_max = portfolio_values.expanding().max()
        drawdowns = portfolio_values - rolling_max
        return abs(drawdowns.min() / rolling_max.iloc[drawdowns.argmin()])
    
    def calculate_portfolio_value(self):
        """Calculate the portfolio value over time"""
        if self.positions is None:
            self.portfolio_value = [self.initial_capital] * len(self.data)
            return
            
        position_series = pd.Series(self.positions, index=self.data.index)
        price_changes = self.data['close'].pct_change()
        
        # Fill NaN values with 0 for first day
        price_changes.iloc[0] = 0
        
        # Calculate strategy returns
        strategy_returns = position_series.shift(1).fillna(0) * price_changes
        
        # Calculate cumulative portfolio value
        cumulative_returns = (1 + strategy_returns).cumprod()
        self.portfolio_value = (self.initial_capital * cumulative_returns).tolist()
    
    @abstractmethod
    def execute(self):
        """Execute the trading strategy"""
        pass 