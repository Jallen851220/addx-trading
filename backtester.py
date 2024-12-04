import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from seo_optimizer import AdvancedTradingBot

class BacktestEngine:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.performance_metrics = {}
        self.trading_bot = AdvancedTradingBot(initial_capital)
        
    async def run_backtest(self, strategy, data, start_date=None, end_date=None):
        """執行回測"""
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trade_history = []
        
        # 篩選日期範圍
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
            
        # 計算技術指標
        data = self.trading_bot.calculate_technical_indicators(data)
        
        # 執行策略
        for timestamp, row in data.iterrows():
            signals = self.trading_bot.generate_advanced_signals(data.loc[:timestamp])
            await self._execute_signals(signals, row, timestamp)
            
        # 計算績效指標
        self._calculate_performance_metrics()
        return self.performance_metrics
    
    async def _execute_signals(self, signals, current_data, timestamp):
        """執行交易信號"""
        for signal in signals:
            if signal['action'] == 'BUY' and self.current_capital > 0:
                price = current_data['Close']
                quantity = (self.current_capital * signal['suggested_size']) / price
                cost = quantity * price
                
                if self.current_capital >= cost:
                    self.current_capital -= cost
                    self.positions[current_data.name] = {
                        'quantity': quantity,
                        'entry_price': price,
                        'entry_time': timestamp,
                        'strategy': signal.get('strategy', 'unknown')
                    }
                    self.trade_history.append({
                        'timestamp': timestamp,
                        'action': 'BUY',
                        'price': price,
                        'quantity': quantity,
                        'value': cost,
                        'strategy': signal.get('strategy', 'unknown'),
                        'confidence': signal.get('confidence', 0)
                    })
                    
            elif signal['action'] == 'SELL' and current_data.name in self.positions:
                position = self.positions[current_data.name]
                price = current_data['Close']
                value = position['quantity'] * price
                
                self.current_capital += value
                profit_loss = value - (position['quantity'] * position['entry_price'])
                holding_period = timestamp - position['entry_time']
                
                self.trade_history.append({
                    'timestamp': timestamp,
                    'action': 'SELL',
                    'price': price,
                    'quantity': position['quantity'],
                    'value': value,
                    'profit_loss': profit_loss,
                    'holding_period': holding_period,
                    'strategy': position['strategy']
                })
                
                del self.positions[current_data.name]
    
    def _calculate_performance_metrics(self):
        """計算績效指標"""
        if not self.trade_history:
            return
        
        trades_df = pd.DataFrame(self.trade_history)
        trades_df.set_index('timestamp', inplace=True)
        
        # 基本指標
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for trade in self.trade_history if trade.get('profit_loss', 0) > 0)
        total_profit_loss = sum(trade.get('profit_loss', 0) for trade in self.trade_history)
        
        # 收益率指標
        returns = trades_df['value'].pct_change()
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        annual_return = total_return * (252 / len(trades_df))
        
        # 風險指標
        daily_returns = trades_df['value'].pct_change()
        volatility = daily_returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - 0.02) / volatility if volatility != 0 else 0
        
        # 回撤指標
        cumulative_returns = (1 + daily_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        # 策略分析
        strategy_performance = {}
        for strategy in trades_df['strategy'].unique():
            strategy_trades = trades_df[trades_df['strategy'] == strategy]
            strategy_performance[strategy] = {
                'total_trades': len(strategy_trades),
                'win_rate': sum(strategy_trades['profit_loss'] > 0) / len(strategy_trades),
                'avg_profit': strategy_trades['profit_loss'].mean()
            }
        
        self.performance_metrics = {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_profit_loss': total_profit_loss,
            'volatility': volatility,
            'strategy_performance': strategy_performance
        }
    
    def plot_equity_curve(self):
        """繪製權益曲線"""
        if not self.trade_history:
            return None
            
        trades_df = pd.DataFrame(self.trade_history)
        trades_df.set_index('timestamp', inplace=True)
        
        cumulative_returns = (1 + trades_df['value'].pct_change()).cumprod()
        
        plt.figure(figsize=(12, 6))
        plt.plot(cumulative_returns.index, cumulative_returns.values)
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Returns')
        plt.grid(True)
        
        return plt.gcf()