# Algorithmic Trading

This project implements a simple algorithmic trading system using various trading strategies. The system fetches market data, applies different trading strategies, and evaluates their performance.

## Features

- Fetch market data using Yahoo Finance
- Implement multiple trading strategies:
  - Moving Average Crossover
  - Mean Reversion
  - Trend Following
  - Combined Strategy (weighted signals from individual strategies)
- Calculate performance metrics (Sharpe Ratio, Max Drawdown, Total Return)
- Visualize portfolio value and trading signals

## Requirements

- Python 3.x
- pandas
- numpy
- yfinance
- matplotlib

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/algorithmic_trading.git
   cd algorithmic_trading
   ```

2. Install the required packages:
   ```bash
   pip install pandas numpy yfinance matplotlib
   ```

## Usage

1. Open the `main.py` file and modify the parameters as needed (e.g., trading symbol, time period).
2. Run the main script:
   ```bash
   python main.py
   ```

3. The script will fetch market data, run the combined trading strategy, and display performance metrics along with visualizations of the portfolio value and trading signals.

## Strategies

### Moving Average Crossover
This strategy uses two moving averages (short-term and long-term) to generate buy and sell signals based on crossovers.

### Mean Reversion
This strategy assumes that asset prices will revert to their mean over time. It generates buy signals when prices are below the lower Bollinger Band and sell signals when prices are above the upper Bollinger Band.

### Trend Following
This strategy aims to capitalize on existing market trends. It generates buy signals when the price breaks above a recent high and sell signals when it breaks below a recent low.

### Combined Strategy
This strategy combines the signals from the individual strategies using specified weights to create a more robust trading signal.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
