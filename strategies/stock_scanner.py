import pandas as pd
import numpy as np
from typing import List, Dict
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import logging
import time
from datetime import datetime, timedelta

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
        
    def get_sp500_tickers(self) -> List[str]:
        """Get a list of S&P 500 tickers"""
        try:
            # Use a reliable list of major stocks
            major_tickers = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK-B', 'LLY', 'V', 'TSM',
                'JPM', 'XOM', 'AVGO', 'MA', 'PG', 'HD', 'CVX', 'ABBV', 'COST', 'MRK',
                'ADBE', 'CSCO', 'ACN', 'MCD', 'CRM', 'BAC', 'NFLX', 'TMO', 'LIN', 'ORCL'
            ]
            return major_tickers
        except Exception as e:
            logger.error(f"Error getting tickers: {str(e)}")
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

    def get_stock_data(self, symbol: str) -> pd.DataFrame:
        """Get stock data with error handling"""
        try:
            stock = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            data = stock.history(start=start_date, end=end_date)
            
            if len(data) < 200:  # Ensure we have enough data
                return None
                
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def calculate_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate key metrics for stock evaluation"""
        try:
            returns = data['Daily_Return'].dropna()
            
            # Risk-adjusted returns
            annualized_return = returns.mean() * 252
            annualized_vol = returns.std() * np.sqrt(252)
            sharpe_ratio = annualized_return / annualized_vol if annualized_vol != 0 else 0
            
            # Trend strength
            price = data['Close']
            trend_strength = (price.iloc[-1] / price.iloc[-20] - 1) * 100
            
            # Momentum
            momentum = data['RSI'].iloc[-1]
            
            # Volume strength
            volume_strength = data['Volume_Ratio'].iloc[-1]
            
            return {
                'sharpe_ratio': sharpe_ratio,
                'trend_strength': trend_strength,
                'momentum': momentum,
                'volume_strength': volume_strength,
                'current_price': data['Close'].iloc[-1],
                'monthly_return': (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return None

    def scan_stocks(self) -> List[Dict]:
        """Scan stocks and identify top opportunities"""
        opportunities = []
        tickers = self.get_sp500_tickers()
        
        for symbol in tickers:
            try:
                logger.info(f"Processing {symbol}...")
                
                # Get stock data
                data = self.get_stock_data(symbol)
                if data is None:
                    continue
                
                # Calculate indicators
                data = self.calculate_technical_indicators(data)
                
                # Calculate metrics
                metrics = self.calculate_metrics(data)
                if metrics is None:
                    continue
                
                # Calculate opportunity score
                score = (
                    metrics['sharpe_ratio'] * 0.35 +
                    metrics['trend_strength'] * 0.25 +
                    (metrics['momentum'] / 100) * 0.20 +
                    metrics['volume_strength'] * 0.20
                )
                
                # Add to opportunities if meets criteria
                if (metrics['sharpe_ratio'] > 1.0 and
                    metrics['trend_strength'] > 0 and
                    metrics['momentum'] > 40):
                    
                    opportunities.append({
                        'symbol': symbol,
                        'metrics': metrics,
                        'score': score
                    })
                
                time.sleep(1)  # Avoid rate limiting
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
                continue
        
        # Sort opportunities by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities[:5]  # Return top 5 opportunities 