import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

class BacktestEngine:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.performance_metrics = {}
        
    def run_backtest(self, strategy, data, start_date=None, end_date=None):
        """執行回測"""
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trade_history = []
        
        # 篩選日期範圍
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
            
        # 執行策略
        for timestamp, row in data.iterrows():
            signals = strategy.generate_signals(data.loc[:timestamp])
            self._execute_signals(signals, row, timestamp)
            
        # 計算績效指標
        self._calculate_performance_metrics()
        return self.performance_metrics
    
    def _execute_signals(self, signals, current_data, timestamp):
        """執行交易信號"""
        for signal in signals:
            if signal['action'] == 'BUY' and self.current_capital > 0:
                price = current_data['Close']
                quantity = (self.current_capital * signal['position_size']) / price
                cost = quantity * price
                
                if self.current_capital >= cost:
                    self.current_capital -= cost
                    self.positions[current_data.name] = {
                        'quantity': quantity,
                        'entry_price': price
                    }
                    self.trade_history.append({
                        'timestamp': timestamp,
                        'action': 'BUY',
                        'price': price,
                        'quantity': quantity,
                        'value': cost
                    })
                    
            elif signal['action'] == 'SELL' and current_data.name in self.positions:
                position = self.positions[current_data.name]
                price = current_data['Close']
                value = position['quantity'] * price
                
                self.current_capital += value
                profit_loss = value - (position['quantity'] * position['entry_price'])
                
                self.trade_history.append({
                    'timestamp': timestamp,
                    'action': 'SELL',
                    'price': price,
                    'quantity': position['quantity'],
                    'value': value,
                    'profit_loss': profit_loss
                })
                
                del self.positions[current_data.name]
    
    def _calculate_performance_metrics(self):
        """計算績效指標"""
        if not self.trade_history:
            return
        
        trades_df = pd.DataFrame(self.trade_history)
        trades_df.set_index('timestamp', inplace=True)
        
        # 計算收益率
        total_profit_loss = sum(trade.get('profit_loss', 0) for trade in self.trade_history)
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        
        # 計算夏普比率
        daily_returns = trades_df['value'].pct_change()
        sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
        
        # 計算最大回撤
        cumulative_returns = (1 + daily_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        self.performance_metrics = {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.trade_history),
            'winning_trades': sum(1 for trade in self.trade_history if trade.get('profit_loss', 0) > 0),
            'total_profit_loss': total_profit_loss
        } 