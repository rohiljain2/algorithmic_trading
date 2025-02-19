from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class TrendFollowing(BaseStrategy):
    def __init__(self, data, lookback=20):
        super().__init__(data)
        self.lookback = lookback
        self.atr_period = 14
        self.risk_per_trade = 0.02  # 2% risk per trade
        
    def execute(self):
        # Calculate trend indicators
        self.calculate_atr()
        self.calculate_adx()
        
        # Calculate breakout levels
        self.data['rolling_high'] = self.data['close'].rolling(window=self.lookback).max()
        self.data['rolling_low'] = self.data['close'].rolling(window=self.lookback).min()
        
        # Generate signals with trend confirmation
        self.data['signal'] = 0
        
        # Create conditions for signals
        buy_condition = (
            (self.data['close'] > self.data['rolling_high'].shift(1)) &  # Breakout
            (self.data['adx'] > 25) &  # Strong trend
            (self.data['close'] > self.data['close'].rolling(50).mean())  # Above 50MA
        )
        
        sell_condition = (
            (self.data['close'] < self.data['rolling_low'].shift(1)) &  # Breakdown
            (self.data['adx'] > 25) &  # Strong trend
            (self.data['close'] < self.data['close'].rolling(50).mean())  # Below 50MA
        )
        
        # Apply signals
        self.data.loc[buy_condition, 'signal'] = 1
        self.data.loc[sell_condition, 'signal'] = -1
        
        # Apply position sizing and risk management
        self.apply_position_sizing()
        
        # Calculate portfolio value
        self.calculate_portfolio_value()
    
    def calculate_atr(self):
        """Calculate Average True Range"""
        high = self.data['high']
        low = self.data['low']
        close = self.data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.data['atr'] = tr.rolling(self.atr_period).mean()
    
    def calculate_adx(self):
        """Calculate Average Directional Index"""
        # Simplified ADX calculation
        self.data['adx'] = abs(self.data['close'].pct_change(14)).rolling(14).mean() * 100
    
    def apply_position_sizing(self):
        """Apply position sizing based on ATR"""
        position = 0
        entry_price = 0
        self.positions = [0] * len(self.data)  # Initialize positions list with zeros
        
        for i in range(len(self.data)):
            if position == 0 and self.data['signal'].iloc[i] != 0:
                position = self.data['signal'].iloc[i]
                entry_price = self.data['close'].iloc[i]
                # Calculate position size based on ATR
                atr = self.data['atr'].iloc[i]
                stop_distance = 2 * atr  # 2 ATR stop loss
                position_size = (self.portfolio_value[-1] if self.portfolio_value else self.initial_capital) * self.risk_per_trade / stop_distance
                position = position * position_size
            elif position != 0:
                # Check for exit conditions
                if (position > 0 and self.data['close'].iloc[i] < entry_price - 2 * self.data['atr'].iloc[i]) or \
                   (position < 0 and self.data['close'].iloc[i] > entry_price + 2 * self.data['atr'].iloc[i]):
                    position = 0
                    
            self.positions[i] = position  # Update position at index i instead of appending
    
    def calculate_portfolio_value(self):
        """Calculate the portfolio value over time"""
        position_series = pd.Series(self.positions)
        price_changes = self.data['close'].pct_change()
        strategy_returns = position_series.shift(1) * price_changes
        
        portfolio_value = self.initial_capital * (1 + strategy_returns).cumprod()
        self.portfolio_value = portfolio_value.tolist() 