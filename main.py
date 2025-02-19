import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from strategies.combined_strategy import CombinedStrategy
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
import time
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Alpaca API configuration
ALPACA_API_KEY = 'PKO90THNEOJKDJJ40VJT'
ALPACA_SECRET_KEY = 'zogV4TVElCrhagyabNJEhoOzQL8cuzhfOriPNWam'
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'  # Paper trading URL

api = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    ALPACA_BASE_URL,
    api_version='v2'
)

class TradingBot:
    def __init__(self, symbols: List[str], weights: Dict[str, float], initial_capital: float = 100000):
        self.symbols = symbols
        self.weights = weights
        self.initial_capital = initial_capital
        self.strategies = {}
        self.positions = {}
        
    def check_market_hours(self) -> bool:
        """Check if the market is open"""
        clock = api.get_clock()
        return clock.is_open
    
    def fetch_current_data(self, symbol: str) -> pd.DataFrame:
        """Fetch recent market data for analysis"""
        end = datetime.now()
        start = end - timedelta(days=730)  # 2 years of data
        data = api.get_bars(
            symbol,
            '1D',
            start.strftime('%Y-%m-%d'),
            end.strftime('%Y-%m-%d'),
            adjustment='raw'
        ).df
        return data
    
    def execute_trade(self, symbol: str, quantity: int, side: str):
        """Execute a trade through Alpaca"""
        try:
            api.submit_order(
                symbol=symbol,
                qty=quantity,
                side=side,
                type='market',
                time_in_force='gtc'
            )
            logger.info(f"Executed {side} order for {quantity} shares of {symbol}")
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
    
    def update_positions(self):
        """Update current positions"""
        try:
            positions = api.list_positions()
            self.positions = {p.symbol: int(p.qty) for p in positions}
        except Exception as e:
            logger.error(f"Error updating positions: {str(e)}")
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        for symbol in self.symbols:
            try:
                # Fetch current market data
                data = self.fetch_current_data(symbol)
                
                # Initialize strategy if not exists
                if symbol not in self.strategies:
                    self.strategies[symbol] = CombinedStrategy(data, self.weights)
                
                # Update strategy with new data
                self.strategies[symbol].update_data(data)
                self.strategies[symbol].execute()
                
                # Get the latest signal
                latest_signal = self.strategies[symbol].data['signal'].iloc[-1]
                
                # Update current positions
                self.update_positions()
                current_position = self.positions.get(symbol, 0)
                
                # Execute trades based on signals
                if latest_signal == 1 and current_position == 0:  # Buy signal
                    self.execute_trade(symbol, 100, 'buy')
                elif latest_signal == -1 and current_position > 0:  # Sell signal
                    self.execute_trade(symbol, current_position, 'sell')
                
            except Exception as e:
                logger.error(f"Error in trading cycle for {symbol}: {str(e)}")

def main():
    # Define trading parameters
    symbols = ['AAPL', 'MSFT', 'GOOGL']  # Example symbols
    weights = {
        'ma_crossover': 0.4,
        'mean_reversion': 0.3,
        'trend_following': 0.3
    }
    
    # Initialize trading bot
    bot = TradingBot(symbols, weights)
    
    logger.info("Starting trading bot...")
    
    while True:
        try:
            # Check if market is open
            if bot.check_market_hours():
                logger.info("Market is open, running trading cycle...")
                bot.run_trading_cycle()
            else:
                logger.info("Market is closed, waiting...")
            
            # Wait for 5 minutes before next cycle
            time.sleep(300)
            
        except KeyboardInterrupt:
            logger.info("Stopping trading bot...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main() 