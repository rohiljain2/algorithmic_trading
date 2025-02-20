# Algorithmic Trading Bot

## Overview

This project implements an algorithmic trading bot that scans the S&P 500 stocks to identify high-quality investment opportunities based on various technical indicators and machine learning models. The bot utilizes the Yahoo Finance API to fetch stock data and calculates key metrics to evaluate potential investments.

## Features

- Fetches current S&P 500 constituents.
- Calculates advanced technical indicators (SMA, EMA, RSI, MACD, etc.).
- Uses machine learning models to predict future stock performance.
- Identifies top investment opportunities based on Sharpe ratio, trend strength, momentum, and volume analysis.
- Outputs the top 5 investment opportunities with detailed metrics.

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

3. When prompted, select the mode:
   - **1** for market scan: The bot will scan the S&P 500 for top investment opportunities.
   - **2** for live trading: (This feature can be implemented in the future.)

## Output

The bot will display the top 5 investment opportunities with the following metrics:
- **Current Price**: The latest price of the stock.
- **Monthly Return**: The percentage return over the last month.
- **Sharpe Ratio**: A measure of risk-adjusted return.
- **Trend Strength**: Indicates the strength of the current trend.
- **Momentum (RSI)**: The Relative Strength Index value.
- **Overall Score**: A composite score based on various metrics.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the contributors of the libraries used in this project.
- Special thanks to the Yahoo Finance API for providing stock data.
