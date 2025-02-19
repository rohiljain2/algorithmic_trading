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
        self.backtest_results = {}
        
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
    
    def backtest(self, start_date: str, end_date: str):
        """
        Backtest strategies on historical data
        start_date, end_date format: 'YYYY-MM-DD'
        """
        logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        for symbol in self.symbols:
            try:
                # Fetch historical data
                data = api.get_bars(
                    symbol,
                    '1D',
                    start_date,
                    end_date,
                    adjustment='raw'
                ).df
                
                # Initialize strategy
                strategy = CombinedStrategy(data, self.weights)
                strategy.execute()
                
                # Calculate metrics
                metrics = self._calculate_backtest_metrics(strategy, data)
                self.backtest_results[symbol] = metrics
                
                # Plot results
                self._plot_backtest_results(symbol, strategy, data)
                
                logger.info(f"Backtest results for {symbol}:")
                logger.info(f"Total Return: {metrics['total_return']:.2%}")
                logger.info(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
                logger.info(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
                
            except Exception as e:
                logger.error(f"Error in backtest for {symbol}: {str(e)}")
    
    def _calculate_backtest_metrics(self, strategy, data):
        """Calculate performance metrics for backtest"""
        # Convert portfolio_value list to pandas Series
        portfolio_values = pd.Series(strategy.portfolio_value, index=data.index)
        returns = portfolio_values.pct_change().dropna()
        
        total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        
        # Calculate max drawdown using Series methods
        peak = portfolio_values.expanding(min_periods=1).max()
        drawdown = (portfolio_values - peak) / peak
        max_drawdown = drawdown.min()
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'daily_returns': returns
        }
    
    def _plot_backtest_results(self, symbol: str, strategy, data):
        """Plot backtest results"""
        plt.figure(figsize=(15, 12))
        
        # Plot portfolio value
        plt.subplot(3, 1, 1)
        plt.plot(strategy.portfolio_value, label='Portfolio Value')
        plt.title(f'Backtest Results - {symbol}')
        plt.legend()
        plt.grid(True)
        
        # Plot asset price and signals
        plt.subplot(3, 1, 2)
        plt.plot(data.index, data['close'], label='Price')
        signals = strategy.data['signal']
        
        # Plot buy signals
        buy_signals = data[signals == 1].index
        if len(buy_signals) > 0:
            plt.plot(buy_signals, data.loc[buy_signals, 'close'], '^', 
                    markersize=10, color='g', label='Buy Signal')
        
        # Plot sell signals
        sell_signals = data[signals == -1].index
        if len(sell_signals) > 0:
            plt.plot(sell_signals, data.loc[sell_signals, 'close'], 'v', 
                    markersize=10, color='r', label='Sell Signal')
        
        plt.legend()
        plt.grid(True)
        
        # Plot daily returns
        plt.subplot(3, 1, 3)
        plt.plot(self.backtest_results[symbol]['daily_returns'], label='Daily Returns')
        plt.title('Daily Returns')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()

def main():
    # Define trading parameters
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    weights = {
        'ma_crossover': 0.4,
        'mean_reversion': 0.3,
        'trend_following': 0.3
    }
    
    # Initialize trading bot
    bot = TradingBot(symbols, weights)
    
    # Ask user for mode
    mode = input("Select mode (1 for backtest, 2 for live trading): ")
    
    if mode == "1":
        # Backtest mode
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")
        bot.backtest(start_date, end_date)
        
        # Allow user to adjust weights based on backtest results
        adjust = input("Would you like to adjust strategy weights? (y/n): ")
        if adjust.lower() == 'y':
            print("Current weights:", weights)
            weights['ma_crossover'] = float(input("Enter new MA Crossover weight (0-1): "))
            weights['mean_reversion'] = float(input("Enter new Mean Reversion weight (0-1): "))
            weights['trend_following'] = float(input("Enter new Trend Following weight (0-1): "))
            
            # Normalize weights
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
            
            # Run backtest again with new weights
            bot = TradingBot(symbols, weights)
            bot.backtest(start_date, end_date)
    
    elif mode == "2":
        # Live trading mode
        logger.info("Starting live trading bot...")
        while True:
            try:
                if bot.check_market_hours():
                    logger.info("Market is open, running trading cycle...")
                    bot.run_trading_cycle()
                else:
                    logger.info("Market is closed, waiting...")
                time.sleep(300)
            except KeyboardInterrupt:
                logger.info("Stopping trading bot...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    main() 