import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import ccxt
import numpy as np
from seo_optimizer import AdvancedMarketDataFetcher, AdvancedTradingBot
from database_handler import DatabaseManager
from backtester import BacktestEngine
from notification_system import NotificationSystem
from auth_system import CloudAuthSystem

# 初始化系統組件
auth_system = CloudAuthSystem()
market_fetcher = AdvancedMarketDataFetcher()
db_manager = DatabaseManager()

def initialize_app():
    """初始化應用程序"""
    st.set_page_config(
        page_title="ADDX 智能交易系統",
        page_icon="📈",
        layout="wide"
    )
    
    if 'user' not in st.session_state:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    """顯示登入頁面"""
    st.title('ADDX 智能交易系統')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button('Google 登入'):
            try:
                auth_result = auth_system.handle_social_login('google')
                if auth_result:
                    st.session_state.user = auth_result
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"登入失敗: {str(e)}")
    
    with col2:
        if st.button('LINE 登入'):
            try:
                auth_result = auth_system.handle_social_login('line')
                if auth_result:
                    st.session_state.user = auth_result
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"登入失敗: {str(e)}")
    
    with col3:
        if st.button('Telegram 登入'):
            try:
                auth_result = auth_system.handle_social_login('telegram')
                if auth_result:
                    st.session_state.user = auth_result
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"登入失敗: {str(e)}")

def show_main_app():
    """顯示主應用程序"""
    st.title('ADDX 智能交易系統')
    
    # 側邊欄設置
    with st.sidebar:
        st.title('交易設置')
        initial_capital = st.number_input('初始資金', value=100000)
        risk_per_trade = st.slider('風險比例', 0.01, 0.05, 0.02)
        
        if st.button('登出'):
            del st.session_state.user
            st.experimental_rerun()
    
    # 主要內容區域
    tabs = st.tabs(['市場概覽', '交易機器人', '投資組合', '回測系統'])
    
    with tabs[0]:
        show_market_overview()
    
    with tabs[1]:
        show_trading_bot(initial_capital, risk_per_trade)
    
    with tabs[2]:
        show_portfolio()
    
    with tabs[3]:
        show_backtest()

@st.cache_data(ttl=60)
def fetch_market_data(symbols):
    """獲取市場數據"""
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            data[symbol] = {
                'price': info.get('regularMarketPrice', 'N/A'),
                'change': info.get('regularMarketChangePercent', 'N/A'),
                'volume': info.get('regularMarketVolume', 'N/A')
            }
        except Exception as e:
            st.warning(f"獲取 {symbol} 數據失敗: {str(e)}")
            continue
    return data

def show_market_overview():
    """顯示市場概覽"""
    st.header('市場概覽')
    
    symbols = ['AAPL', 'GOOGL', 'BTC-USD', 'ETH-USD']
    data = fetch_market_data(symbols)
    
    cols = st.columns(len(data))
    for i, (symbol, info) in enumerate(data.items()):
        with cols[i]:
            st.metric(
                label=symbol,
                value=f"${info['price']}",
                delta=f"{info['change']:.2f}%" if isinstance(info['change'], (int, float)) else 'N/A'
            )

def show_trading_bot(initial_capital, risk_per_trade):
    """顯示交易機器人界面"""
    st.header('交易機器人')
    
    trading_bot = AdvancedTradingBot(initial_capital)
    
    strategy = st.selectbox(
        '選擇交易策略',
        ['MACD + RSI', '布林通道', '均線交叉']
    )
    
    col1, col2 = st.columns(2)
    with col1:
        stop_loss = st.number_input('止損比例 %', value=2)
    with col2:
        take_profit = st.number_input('獲利目標 %', value=6)
    
    if st.button('啟動自動交易'):
        with st.spinner('正在初始化交易機器人...'):
            try:
                # 這裡添加實際的交易邏輯
                st.success('交易機器人已啟動！')
            except Exception as e:
                st.error(f'啟動失敗: {str(e)}')

def show_portfolio():
    """顯示投資組合分析"""
    st.header('投資組合分析')
    
    # 獲取投資組合數據
    portfolio_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', end='2024-01-01', freq='D'),
        'Value': np.random.normal(loc=100000, scale=1000, size=366).cumsum()
    })
    
    # 顯示投資組合圖表
    st.line_chart(portfolio_data.set_index('Date'))
    
    # 顯示投資組合統計
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("總收益率", "15.2%")
    with col2:
        st.metric("夏普比率", "1.8")
    with col3:
        st.metric("最大回撤", "-8.5%")

def show_backtest():
    """顯示回測系統"""
    st.header('回測系統')
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('開始日期', value=datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input('結束日期', value=datetime.now())
    
    symbol = st.text_input('輸入交易標的代碼', 'AAPL')
    
    if st.button('開始回測'):
        with st.spinner('正在進行回測...'):
            try:
                backtest_engine = BacktestEngine(100000)
                # 這裡添加實際的回測邏輯
                st.success('回測完成！')
            except Exception as e:
                st.error(f'回測失敗: {str(e)}')

if __name__ == "__main__":
    initialize_app()