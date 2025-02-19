from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class MovingAverageCrossover(BaseStrategy):
    def __init__(self, data, short_window=50, long_window=200):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window
        self.stop_loss = 0.02  # 2% stop loss
        self.take_profit = 0.04  # 4% take profit
        
    def execute(self):
        # Calculate moving averages
        self.data['short_mavg'] = self.data['close'].rolling(window=self.short_window).mean()
        self.data['long_mavg'] = self.data['close'].rolling(window=self.long_window).mean()
        
        # Calculate additional technical indicators
        self.data['volatility'] = self.data['close'].rolling(window=20).std()
        self.data['rsi'] = self.calculate_rsi(self.data['close'])
        
        # Generate signals with confirmation
        self.data['signal'] = 0
        
        # Create conditions for buy signals
        conditions = (
            (self.data['short_mavg'] > self.data['long_mavg']) &  # MA crossover
            (self.data['rsi'] < 70) &  # Not overbought
            (self.data['close'] > self.data['close'].rolling(50).mean())  # Price above 50MA
        )
        
        # Apply signals where conditions are met and after short_window period
        self.data.loc[conditions & (self.data.index >= self.data.index[self.short_window]), 'signal'] = 1
        
        # Apply risk management
        self.apply_risk_management()
        
        # Calculate positions and portfolio value
        self.calculate_portfolio_value()
        
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def apply_risk_management(self):
        """Apply stop loss and take profit levels"""
        position = 0
        entry_price = 0
        self.positions = [0] * len(self.data)  # Initialize positions list with zeros
        
        for i in range(len(self.data)):
            if position == 0 and self.data['signal'].iloc[i] == 1:
                position = 1
                entry_price = self.data['close'].iloc[i]
            elif position == 1:
                current_price = self.data['close'].iloc[i]
                pnl = (current_price - entry_price) / entry_price
                
                if pnl <= -self.stop_loss or pnl >= self.take_profit:
                    position = 0
                    
            self.positions[i] = position  # Update position at index i instead of appending
    
    def calculate_portfolio_value(self):
        """Calculate the portfolio value over time"""
        position_series = pd.Series(self.positions)
        price_changes = self.data['close'].pct_change()
        strategy_returns = position_series.shift(1) * price_changes
        
        portfolio_value = self.initial_capital * (1 + strategy_returns).cumprod()
        self.portfolio_value = portfolio_value.tolist() 