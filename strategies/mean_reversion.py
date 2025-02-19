from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class MeanReversion(BaseStrategy):
    def __init__(self, data, mean_window=20, entry_std=2.0):
        super().__init__(data)
        self.mean_window = mean_window
        self.entry_std = entry_std
        self.stop_loss = 0.02
        self.take_profit = 0.03
        
    def execute(self):
        # Calculate mean and standard deviation
        self.data['mean'] = self.data['close'].rolling(window=self.mean_window).mean()
        self.data['std'] = self.data['close'].rolling(window=self.mean_window).std()
        
        # Calculate z-score
        self.data['z_score'] = (self.data['close'] - self.data['mean']) / self.data['std']
        
        # Calculate Bollinger Bands
        self.data['upper_band'] = self.data['mean'] + (self.entry_std * self.data['std'])
        self.data['lower_band'] = self.data['mean'] - (self.entry_std * self.data['std'])
        
        # Generate signals
        self.data['signal'] = 0
        
        # Create conditions for signals
        buy_condition = (self.data['close'] < self.data['lower_band'])
        sell_condition = (self.data['close'] > self.data['upper_band'])
        
        # Apply signals
        self.data.loc[buy_condition, 'signal'] = 1
        self.data.loc[sell_condition, 'signal'] = -1
        
        # Apply volume filter
        self.data['volume_ma'] = self.data['volume'].rolling(window=20).mean()
        self.data.loc[self.data['volume'] < self.data['volume_ma'], 'signal'] = 0
        
        # Apply risk management
        self.apply_risk_management()
        
        # Calculate portfolio value
        self.calculate_portfolio_value()
    
    def apply_risk_management(self):
        """Apply position sizing and risk management"""
        position = 0
        entry_price = 0
        self.positions = [0] * len(self.data)  # Initialize positions list with zeros
        
        for i in range(len(self.data)):
            if position == 0:
                if self.data['signal'].iloc[i] == 1:
                    position = 1
                    entry_price = self.data['close'].iloc[i]
                elif self.data['signal'].iloc[i] == -1:
                    position = -1
                    entry_price = self.data['close'].iloc[i]
            else:
                current_price = self.data['close'].iloc[i]
                pnl = abs((current_price - entry_price) / entry_price)
                
                if pnl >= self.take_profit or pnl <= -self.stop_loss:
                    position = 0
                    
            self.positions[i] = position  # Update position at index i instead of appending
    
    def calculate_portfolio_value(self):
        """Calculate the portfolio value over time"""
        position_series = pd.Series(self.positions)
        price_changes = self.data['close'].pct_change()
        strategy_returns = position_series.shift(1) * price_changes
        
        portfolio_value = self.initial_capital * (1 + strategy_returns).cumprod()
        self.portfolio_value = portfolio_value.tolist() 