import streamlit as st
from streamlit_firebase import FirebaseApp
import pandas as pd
from datetime import datetime
import yfinance as yf
import ccxt
import numpy as np

# 初始化 Firebase
firebase_app = FirebaseApp.create(
    api_key="AIzaSyADDX_default_config",
    project_id="addx-trading",
    auth_domain="addx-trading.firebaseapp.com"
)

def initialize_app():
    """初始化應用程序"""
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
            user = firebase_app.auth.sign_in_with_google()
            if user:
                st.session_state.user = user
                st.experimental_rerun()
    
    with col2:
        if st.button('LINE 登入'):
            user = firebase_app.auth.sign_in_with_line()
            if user:
                st.session_state.user = user
                st.experimental_rerun()
    
    with col3:
        if st.button('Telegram 登入'):
            user = firebase_app.auth.sign_in_with_telegram()
            if user:
                st.session_state.user = user
                st.experimental_rerun()

def show_main_app():
    """顯示主應用程序"""
    st.title(f'歡迎回來, {st.session_state.user.display_name}')
    
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
        show_trading_bot()
    
    with tabs[2]:
        show_portfolio()
    
    with tabs[3]:
        show_backtest()

def show_market_overview():
    """顯示市場概覽"""
    st.header('市場概覽')
    
    # 使用 yfinance 獲取實時數據
    symbols = ['AAPL', 'GOOGL', 'BTC-USD', 'ETH-USD']
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
        except:
            continue
    
    # 顯示數據
    cols = st.columns(len(data))
    for i, (symbol, info) in enumerate(data.items()):
        with cols[i]:
            st.metric(
                label=symbol,
                value=f"${info['price']}",
                delta=f"{info['change']:.2f}%"
            )

def show_trading_bot():
    """顯示交易機器人界面"""
    st.header('交易機器人')
    
    strategy = st.selectbox(
        '選擇交易策略',
        ['MACD + RSI', '布林通道', '均線交叉']
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input('止損比例 %', value=2)
    with col2:
        st.number_input('獲利目標 %', value=6)
    
    if st.button('啟動自動交易'):
        st.success('交易機器人已啟動！')

def show_portfolio():
    """顯示投資組合分析"""
    st.header('投資組合分析')
    
    # 模擬投資組合數據
    portfolio_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', end='2024-01-01', freq='D'),
        'Value': np.random.normal(loc=100000, scale=1000, size=366).cumsum()
    })
    
    st.line_chart(portfolio_data.set_index('Date'))

def show_backtest():
    """顯示回測系統"""
    st.header('回測系統')
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('開始日期')
    with col2:
        end_date = st.date_input('結束日期')
    
    symbol = st.text_input('輸入交易標的代碼', 'AAPL')
    
    if st.button('開始回測'):
        st.info('正在進行回測...')
        # 這裡添加回測邏輯

if __name__ == "__main__":
    initialize_app()