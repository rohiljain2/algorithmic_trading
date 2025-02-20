# Algorithmic Trading Bot

## Overview

This project implements an algorithmic trading bot that scans the S&P 500 stocks to identify high-quality investment opportunities based on various technical indicators and machine learning models. The bot utilizes the Yahoo Finance API to fetch stock data and calculates key metrics to evaluate potential investments. Additionally, it employs Monte Carlo simulations to predict future stock price movements and assess risk.

## Features

- Fetches current S&P 500 constituents.
- Calculates advanced technical indicators (SMA, EMA, RSI, MACD, etc.).
- Uses machine learning models to predict future stock performance.
- Identifies top investment opportunities based on Sharpe ratio, trend strength, momentum, and volume analysis.
- Performs Monte Carlo simulations to simulate potential future price paths.
- Outputs the top 5 investment opportunities with detailed metrics and simulation results.

## Requirements

- Python 3.7 or higher
- Required Python packages:
  - `pandas`
  - `numpy`
  - `yfinance`
  - `scikit-learn`
  - `matplotlib`
  - `logging`

You can install the required packages using pip:

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/algorithmic_trading.git
   cd algorithmic_trading
   ```

2. Install the required packages as mentioned above.

## Usage

1. Open a terminal and navigate to the project directory.
2. Run the main script:

   ```bash
   python main.py
   ```

3. The bot will automatically scan the S&P 500 for the top 5 investment opportunities and display the results, including Monte Carlo simulation metrics.

## Output

The bot will display the top 5 investment opportunities with the following metrics:
- **Current Price**: The latest price of the stock.
- **Monthly Return**: The percentage return over the last month.
- **Sharpe Ratio**: A measure of risk-adjusted return.
- **Trend Strength**: Indicates the strength of the current trend.
- **Momentum (RSI)**: The Relative Strength Index value.
- **Expected Return (1Y)**: The expected return based on Monte Carlo simulations.
- **Probability of Positive Return**: The likelihood of a positive return based on simulations.
- **95% VaR**: The Value at Risk at the 95% confidence level.
- **Max Drawdown Risk**: The maximum observed loss from a peak to a trough.
- **Overall Score**: A composite score based on various metrics.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the contributors of the libraries used in this project.
- Special thanks to the Yahoo Finance API for providing stock data.
