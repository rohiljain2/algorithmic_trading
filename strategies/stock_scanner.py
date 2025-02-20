import pandas as pd
import numpy as np
from typing import List, Dict
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime, timedelta
import requests
from .monte_carlo import MonteCarloSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockScanner:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            random_state=42
        )
        self.monte_carlo = MonteCarloSimulator()
        
    def get_sp500_tickers(self) -> List[str]:
        """Get all S&P 500 tickers"""
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_table = tables[0]
            return sp500_table['Symbol'].tolist()
        except Exception as e:
            logger.error(f"Error fetching S&P 500 tickers: {str(e)}")
            return []

    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = data.copy()
        
        # Price-based indicators
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Momentum
        df['RSI'] = self.calculate_rsi(df['Close'])
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        
        # Volatility
        df['Daily_Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
        
        # Volume
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        return df.dropna()

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def process_stock(self, symbol: str) -> Dict:
        """Process individual stock data"""
        try:
            stock = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            data = stock.history(start=start_date, end=end_date)
            
            if len(data) < 200:
                return None
                
            data = self.calculate_technical_indicators(data)
            
            returns = data['Daily_Return'].dropna()
            
            # Calculate metrics
            annualized_return = returns.mean() * 252
            annualized_vol = returns.std() * np.sqrt(252)
            sharpe_ratio = annualized_return / annualized_vol if annualized_vol != 0 else 0
            trend_strength = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
            momentum = data['RSI'].iloc[-1]
            volume_strength = data['Volume_Ratio'].iloc[-1]
            
            metrics = {
                'sharpe_ratio': sharpe_ratio,
                'trend_strength': trend_strength,
                'momentum': momentum,
                'volume_strength': volume_strength,
                'current_price': data['Close'].iloc[-1],
                'monthly_return': (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
            }
            
            # Add Monte Carlo simulation
            price_paths, mc_metrics = self.monte_carlo.simulate_prices(data)
            
            metrics.update({
                'expected_return': mc_metrics['expected_return'],
                'var_95': mc_metrics['var_95'],
                'prob_positive': mc_metrics['prob_positive'],
                'max_drawdown': mc_metrics['max_drawdown']
            })
            
            # Update scoring to include Monte Carlo metrics
            score = (
                metrics['sharpe_ratio'] * 0.25 +
                metrics['trend_strength'] * 0.20 +
                (metrics['momentum'] / 100) * 0.15 +
                metrics['volume_strength'] * 0.15 +
                metrics['prob_positive'] * 0.15 +
                (1 + metrics['expected_return']) * 0.10
            )
            
            # Update filtering criteria
            if (metrics['sharpe_ratio'] > 1.0 and
                metrics['trend_strength'] > 0 and
                metrics['momentum'] > 40 and
                metrics['prob_positive'] > 0.55 and  # Added probability threshold
                metrics['var_95'] > -0.2):  # Added VaR threshold
                
                return {
                    'symbol': symbol,
                    'metrics': metrics,
                    'score': score,
                    'price_paths': price_paths
                }
                
        except Exception:
            return None

    def scan_stocks(self) -> List[Dict]:
        """Scan stocks and identify top opportunities using parallel processing"""
        tickers = self.get_sp500_tickers()
        opportunities = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(self.process_stock, symbol): symbol 
                              for symbol in tickers}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result is not None:
                    opportunities.append(result)
        
        # Sort opportunities by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        return opportunities[:5]  # Return top 5 opportunities 