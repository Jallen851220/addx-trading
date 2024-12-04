import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
import talib
from sklearn.ensemble import RandomForestClassifier
from scipy import stats

class AdvancedMarketDataFetcher:
    def __init__(self):
        self.stock_api = yf
        self.crypto_exchange = ccxt.binance()
        self.futures_exchange = ccxt.binanceusdm()
        
    async def get_market_depth(self, symbol, market_type):
        try:
            if market_type == 'crypto':
                order_book = self.crypto_exchange.fetch_order_book(symbol)
                return {
                    'bids': order_book['bids'][:10],
                    'asks': order_book['asks'][:10]
                }
        except Exception as e:
            print(f"Error fetching market depth: {e}")
            return None

    async def get_historical_data(self, symbol, timeframe='1d', limit=100):
        try:
            if timeframe == '1d':
                data = self.stock_api.download(symbol, 
                                             start=(datetime.now() - timedelta(days=limit)).strftime('%Y-%m-%d'),
                                             end=datetime.now().strftime('%Y-%m-%d'))
                return data
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None

class AdvancedTradingBot:
    def __init__(self, initial_capital):
        self.capital = initial_capital
        self.positions = {}
        self.risk_per_trade = 0.02
        self.ml_model = RandomForestClassifier(n_estimators=100)
        
    def calculate_technical_indicators(self, df):
        # 基礎指標
        df['SMA_20'] = talib.SMA(df['Close'].values, timeperiod=20)
        df['SMA_50'] = talib.SMA(df['Close'].values, timeperiod=50)
        df['RSI'] = talib.RSI(df['Close'].values, timeperiod=14)
        df['MACD'], df['Signal'], df['Hist'] = talib.MACD(df['Close'].values)
        
        # 布林通道
        df['BB_upper'], df['BB_middle'], df['BB_lower'] = talib.BBANDS(
            df['Close'].values, timeperiod=20, nbdevup=2, nbdevdn=2)
        
        # 動量指標
        df['MOM'] = talib.MOM(df['Close'].values, timeperiod=10)
        df['ROC'] = talib.ROC(df['Close'].values, timeperiod=10)
        
        # 成交量指標
        df['OBV'] = talib.OBV(df['Close'].values, df['Volume'].values)
        df['AD'] = talib.AD(df['High'].values, df['Low'].values, 
                           df['Close'].values, df['Volume'].values)
        
        return df

    def calculate_risk_metrics(self, df):
        # 計算波動率
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
        
        # 計算夏普比率
        risk_free_rate = 0.02  # 假設無風險利率為2%
        excess_returns = df['Returns'] - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
        # 計算最大回撤
        rolling_max = df['Close'].rolling(window=252, min_periods=1).max()
        daily_drawdown = df['Close']/rolling_max - 1.0
        max_drawdown = daily_drawdown.rolling(window=252, min_periods=1).min()
        
        return {
            'volatility': df['Volatility'].iloc[-1],
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown.iloc[-1]
        }

    def generate_advanced_signals(self, df):
        signals = []
        
        # 技術分析信號
        if (df['RSI'].iloc[-1] < 30 and 
            df['Close'].iloc[-1] > df['BB_lower'].iloc[-1] and
            df['MACD'].iloc[-1] > df['Signal'].iloc[-1]):
            
            signals.append({
                'action': 'BUY',
                'confidence': 0.8,
                'reason': '多重指標顯示超賣',
                'suggested_size': self.calculate_position_size(df['Close'].iloc[-1])
            })
            
        # 機器學習預測
        prediction = self.predict_price_movement(df)
        if prediction['direction'] == 1 and prediction['probability'] > 0.7:
            signals.append({
                'action': 'BUY',
                'confidence': prediction['probability'],
                'reason': 'ML模型預測上漲',
                'suggested_size': self.calculate_position_size(df['Close'].iloc[-1])
            })
            
        return signals

    def predict_price_movement(self, df):
        # 準備特徵
        features = ['RSI', 'MOM', 'ROC', 'Volatility']
        X = df[features].dropna()
        
        # 準備標籤（1表示上漲，0表示下跌）
        y = (df['Close'].shift(-1) > df['Close']).astype(int)
        y = y[:-1]  # 移除最後一個NA值
        
        # 訓練模型
        self.ml_model.fit(X[:-1], y)
        
        # 預測下一個時間點
        latest_features = X.iloc[-1:]
        prediction = self.ml_model.predict(latest_features)
        probability = self.ml_model.predict_proba(latest_features)
        
        return {
            'direction': prediction[0],
            'probability': max(probability[0])
        }

    def optimize_portfolio(self, assets_data):
        # 使用現代投資組合理論優化配置
        returns = pd.DataFrame({asset: data['Returns'] 
                              for asset, data in assets_data.items()})
        
        # 計算預期收益和協方差矩陣
        mu = returns.mean()
        cov = returns.cov()
        
        # 使用蒙地卡羅模擬找出最優配置
        num_portfolios = 1000
        results = []
        
        for _ in range(num_portfolios):
            weights = np.random.random(len(assets_data))
            weights /= np.sum(weights)
            
            portfolio_return = np.sum(mu * weights)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            
            results.append({
                'weights': weights,
                'return': portfolio_return,
                'risk': portfolio_risk,
                'sharpe': (portfolio_return - 0.02) / portfolio_risk
            })
            
        # 返回夏普比率最高的配置
        optimal_portfolio = max(results, key=lambda x: x['sharpe'])
        return optimal_portfolio