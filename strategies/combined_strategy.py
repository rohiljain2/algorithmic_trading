from .base_strategy import BaseStrategy
from .moving_average_crossover import MovingAverageCrossover
from .mean_reversion import MeanReversion
from .trend_following import TrendFollowing
import pandas as pd
import numpy as np

class CombinedStrategy(BaseStrategy):
    def __init__(self, data, weights=None):
        super().__init__(data)
        self.weights = weights or {
            'ma_crossover': 0.4,
            'mean_reversion': 0.3,
            'trend_following': 0.3
        }
        
        # Initialize individual strategies
        self.ma_strategy = MovingAverageCrossover(data.copy())
        self.mr_strategy = MeanReversion(data.copy())
        self.tf_strategy = TrendFollowing(data.copy())
        
        # Validation of weights
        if abs(sum(self.weights.values()) - 1.0) > 0.0001:
            raise ValueError("Strategy weights must sum to 1.0")
    
    def execute(self):
        try:
            # Execute individual strategies
            self.ma_strategy.execute()
            self.mr_strategy.execute()
            self.tf_strategy.execute()
            
            # Combine signals using weights
            self.data['combined_signal'] = (
                self.weights['ma_crossover'] * self.ma_strategy.data['signal'] +
                self.weights['mean_reversion'] * self.mr_strategy.data['signal'] +
                self.weights['trend_following'] * self.tf_strategy.data['signal']
            )
            
            # Apply position thresholds
            self.data['signal'] = 0
            self.data.loc[self.data['combined_signal'] > 0.3, 'signal'] = 1
            self.data.loc[self.data['combined_signal'] < -0.3, 'signal'] = -1
            
            # Apply risk management
            self.apply_risk_management()
            
            # Calculate portfolio value
            self.calculate_portfolio_value()
            
        except Exception as e:
            print(f"Error in strategy execution: {str(e)}")
            raise
    
    def apply_risk_management(self):
        """Apply position sizing and risk management"""
        self.positions = [0] * len(self.data)
        position = 0
        entry_price = 0
        stop_loss = 0.02
        take_profit = 0.04
        
        for i in range(len(self.data)):
            if position == 0 and self.data['signal'].iloc[i] != 0:
                position = self.data['signal'].iloc[i]
                entry_price = self.data['close'].iloc[i]
            elif position != 0:
                current_price = self.data['close'].iloc[i]
                pnl = (current_price - entry_price) / entry_price
                
                if abs(pnl) >= take_profit or abs(pnl) <= -stop_loss:
                    position = 0
                    
            self.positions[i] = position
    
    def get_strategy_metrics(self):
        """Get individual strategy metrics"""
        try:
            metrics = {
                'combined': self.calculate_metrics(),
                'ma_crossover': self.ma_strategy.calculate_metrics(),
                'mean_reversion': self.mr_strategy.calculate_metrics(),
                'trend_following': self.tf_strategy.calculate_metrics()
            }
            return metrics
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return {
                'combined': {'sharpe_ratio': 0, 'max_drawdown': 0, 'total_return': 0},
                'ma_crossover': {'sharpe_ratio': 0, 'max_drawdown': 0, 'total_return': 0},
                'mean_reversion': {'sharpe_ratio': 0, 'max_drawdown': 0, 'total_return': 0},
                'trend_following': {'sharpe_ratio': 0, 'max_drawdown': 0, 'total_return': 0}
            } 