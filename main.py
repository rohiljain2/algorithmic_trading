import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from strategies.combined_strategy import CombinedStrategy
import matplotlib.pyplot as plt

def fetch_data(symbol='SPY', period='2y'):
    """Fetch market data using yfinance"""
    stock = yf.Ticker(symbol)
    data = stock.history(period=period)
    
    # Standardize column names to lowercase
    data.columns = data.columns.str.lower()
    return data

def evaluate_strategy(strategy, data):
    """Evaluate strategy performance and print metrics"""
    metrics = strategy.get_strategy_metrics()
    
    print("\nStrategy Performance Metrics:")
    print("=" * 50)
    
    for strategy_name, strategy_metrics in metrics.items():
        print(f"\n{strategy_name.upper()} Strategy:")
        print(f"Sharpe Ratio: {strategy_metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {strategy_metrics['max_drawdown']:.2%}")
        print(f"Total Return: {strategy_metrics['total_return']:.2%}")

def plot_performance(strategy, data):
    """Plot strategy performance"""
    plt.figure(figsize=(15, 10))
    
    # Plot portfolio value
    plt.subplot(2, 1, 1)
    portfolio_series = pd.Series(strategy.portfolio_value, index=data.index)
    plt.plot(portfolio_series)
    plt.title('Portfolio Value Over Time')
    plt.grid(True)
    
    # Plot asset price and signals
    plt.subplot(2, 1, 2)
    plt.plot(data.index, data['close'], label='Asset Price')
    
    # Plot buy and sell signals
    signals = strategy.data['signal']
    buy_signals = data[signals == 1].index
    sell_signals = data[signals == -1].index
    
    if len(buy_signals) > 0:
        plt.plot(buy_signals, data.loc[buy_signals, 'close'], '^', 
                markersize=10, color='g', label='Buy Signal')
    if len(sell_signals) > 0:
        plt.plot(sell_signals, data.loc[sell_signals, 'close'], 'v', 
                markersize=10, color='r', label='Sell Signal')
    
    plt.title('Trading Signals')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    try:
        # Fetch market data
        print("Fetching market data...")
        data = fetch_data(symbol='SPY', period='2y')
        
        if data.empty:
            raise ValueError("No data received from API")
        
        # Initialize and run combined strategy
        print("Running combined strategy...")
        weights = {
            'ma_crossover': 0.4,
            'mean_reversion': 0.3,
            'trend_following': 0.3
        }
        
        strategy = CombinedStrategy(data, weights=weights)
        strategy.execute()
        
        # Evaluate and plot results
        evaluate_strategy(strategy, data)
        plot_performance(strategy, data)
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 