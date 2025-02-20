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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def main():
    # Initialize scanner
    scanner = StockScanner()
    
    # Scan for opportunities
    logger.info("Scanning market for top opportunities...")
    opportunities = scanner.scan_stocks()
    
    if opportunities:
        print("\n=== Top 5 Investment Opportunities ===")
        print("=====================================")
        
        for i, opp in enumerate(opportunities, 1):
            metrics = opp['metrics']
            print(f"\n{i}. {opp['symbol']}")
            print(f"Current Price: ${metrics['current_price']:.2f}")
            print(f"Monthly Return: {metrics['monthly_return']:.1f}%")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Trend Strength: {metrics['trend_strength']:.1f}%")
            print(f"Momentum (RSI): {metrics['momentum']:.1f}")
            print(f"Overall Score: {opp['score']:.2f}")
            print("-" * 40)
    else:
        print("\nNo high-quality opportunities found.")

if __name__ == "__main__":
    main()