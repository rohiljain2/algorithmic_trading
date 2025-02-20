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
from strategies.stock_scanner import StockScanner

# Configure logging and pandas display
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# Alpaca API configuration
ALPACA_API_KEY = 'YOUR_ALPACA_API_KEY'
ALPACA_SECRET_KEY = 'YOUR_ALPACA_SECRET_KEY'
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'  # Paper trading URL

api = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    ALPACA_BASE_URL,
    api_version='v2'
)

class TradingBot:
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.scanner = StockScanner()
        self.positions = {}
        self.backtest_results = {}
        self.top_opportunities = []
        
    def scan_market(self):
        """Scan market for best opportunities"""
        try:
            # Get S&P 500 symbols
            logger.info("Fetching S&P 500 symbols...")
            universe = self.scanner.get_sp500_symbols()  # Changed from get_universe to get_sp500_symbols
            
            # Scan stocks
            logger.info(f"Scanning {len(universe)} stocks...")
            opportunities = self.scanner.scan_stocks(universe)
            
            # Filter for high Sharpe ratio stocks
            self.top_opportunities = [
                opp for opp in opportunities 
                if opp['metrics']['sharpe_ratio'] > 1.5  # Lowered threshold for testing
            ][:10]  # Top 10 stocks
            
            logger.info(f"Found {len(self.top_opportunities)} high-quality opportunities")
            return self.top_opportunities
            
        except Exception as e:
            logger.error(f"Error in scan_market: {str(e)}")
            return []
    
    # ... (rest of the TradingBot class remains unchanged)

def plot_monte_carlo(symbol: str, price_paths: np.ndarray, current_price: float):
    """Plot Monte Carlo simulation paths"""
    plt.figure(figsize=(12, 6))
    
    # Plot a subset of paths for better visibility
    num_paths_to_plot = 100
    step = len(price_paths[0]) // num_paths_to_plot
    
    # Plot simulation paths
    for path in price_paths.T[::step]:
        plt.plot(path, color='blue', alpha=0.1)
    
    # Plot mean path
    mean_path = price_paths.mean(axis=1)
    plt.plot(mean_path, color='red', linewidth=2, label='Mean Path')
    
    # Plot confidence intervals
    percentile_5 = np.percentile(price_paths, 5, axis=1)
    percentile_95 = np.percentile(price_paths, 95, axis=1)
    
    plt.fill_between(range(len(mean_path)), percentile_5, percentile_95, 
                     color='gray', alpha=0.2, label='90% Confidence Interval')
    
    plt.axhline(y=current_price, color='green', linestyle='--', label='Current Price')
    
    plt.title(f'Monte Carlo Simulation - {symbol} Price Projections (1 Year)')
    plt.xlabel('Trading Days')
    plt.ylabel('Stock Price ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    plt.savefig(f'monte_carlo_{symbol}.png')
    plt.close()

def main():
    scanner = StockScanner()
    logger.info("Scanning S&P 500 stocks...")
    opportunities = scanner.scan_stocks()
    
    if opportunities:
        print("\n=== Top 5 Investment Opportunities ===")
        print("=====================================")
        
        for i, opp in enumerate(opportunities, 1):
            metrics = opp['metrics']
            symbol = opp['symbol']
            
            print(f"\n{i}. {symbol}")
            print(f"Current Price: ${metrics['current_price']:.2f}")
            print(f"Monthly Return: {metrics['monthly_return']:.1f}%")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Trend Strength: {metrics['trend_strength']:.1f}%")
            print(f"Momentum (RSI): {metrics['momentum']:.1f}")
            
            print("\nMonte Carlo Simulation Results:")
            print(f"Expected Return (1Y): {metrics['expected_return']*100:.1f}%")
            print(f"Probability of Positive Return: {metrics['prob_positive']*100:.1f}%")
            print(f"95% VaR: {metrics['var_95']*100:.1f}%")
            print(f"Max Drawdown Risk: {metrics['max_drawdown']*100:.1f}%")
            print(f"Overall Score: {opp['score']:.2f}")
            
            # Plot Monte Carlo simulation if available
            if 'price_paths' in opp:
                plot_monte_carlo(symbol, opp['price_paths'], metrics['current_price'])
                print(f"\nMonte Carlo simulation plot saved as 'monte_carlo_{symbol}.png'")
            
            print("-" * 40)
    else:
        print("\nNo high-quality opportunities found.")

if __name__ == "__main__":
    main()