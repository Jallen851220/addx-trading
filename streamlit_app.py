import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def main():
    st.set_page_config(
        page_title="ADDX 智能交易系統",
        page_icon="📈",
        layout="wide"
    )
    
    st.title('ADDX 智能交易系統')
    
    # 側邊欄設置
    with st.sidebar:
        st.title('設置')
        initial_capital = st.number_input('初始資金', value=100000, min_value=1000)
        risk_per_trade = st.slider('風險比例 (%)', 1, 5, 2)
    
    # 主要內容
    tabs = st.tabs(['市場概覽', '交易機器人', '投資組合', '回測系統'])
    
    with tabs[0]:
        show_market_overview()
    
    with tabs[1]:
        show_trading_bot(initial_capital, risk_per_trade)
    
    with tabs[2]:
        show_portfolio()
    
    with tabs[3]:
        show_backtest()

def show_market_overview():
    st.header('市場概覽')
    
    # 市場數據展示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="AAPL", value="$150", delta="2.5%")
    with col2:
        st.metric(label="BTC/USD", value="$45,000", delta="-1.2%")
    with col3:
        st.metric(label="ETH/USD", value="$3,000", delta="0.8%")
    with col4:
        st.metric(label="S&P 500", value="4,500", delta="1.5%")
    
    # 市場趨勢圖
    st.subheader('市場趨勢')
    chart_data = pd.DataFrame(
        np.random.randn(30, 4).cumsum(axis=0),
        columns=['AAPL', 'BTC', 'ETH', 'S&P 500']
    )
    st.line_chart(chart_data)

def show_trading_bot(initial_capital, risk_per_trade):
    st.header('交易機器人')
    
    col1, col2 = st.columns(2)
    with col1:
        strategy = st.selectbox(
            '選擇交易策略',
            ['MACD + RSI', '布林通道', '均線交叉']
        )
        
        st.number_input('止損比例 (%)', value=2)
        st.number_input('獲利目標 (%)', value=6)
    
    with col2:
        st.selectbox('交易標的', ['AAPL', 'BTC/USD', 'ETH/USD'])
        st.number_input('每筆交易金額', value=initial_capital * (risk_per_trade/100))
    
    if st.button('啟動自動交易'):
        with st.spinner('初始化交易機器人...'):
            st.success('交易機器人已啟動！')
            st.info(f'使用策略: {strategy}')
            st.info(f'風險控制: {risk_per_trade}%')

def show_portfolio():
    st.header('投資組合分析')
    
    # 投資組合概覽
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="總資產", value="$150,000", delta="15.2%")
    with col2:
        st.metric(label="當日盈虧", value="$2,500", delta="1.8%")
    with col3:
        st.metric(label="持倉數量", value="5")
    
    # 資產配置圖
    st.subheader('資產配置')
    portfolio_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', end='2024-01-01', freq='D'),
        'Value': np.random.normal(loc=100000, scale=1000, size=366).cumsum()
    })
    st.line_chart(portfolio_data.set_index('Date'))

def show_backtest():
    st.header('回測系統')
    
    col1, col2 = st.columns(2)
    with col1:
        st.date_input('開始日期', value=datetime.now() - timedelta(days=365))
    with col2:
        st.date_input('結束日期', value=datetime.now())
    
    st.selectbox('選擇策略', ['MACD + RSI', '布林通道', '均線交叉'])
    st.multiselect('選擇交易標的', ['AAPL', 'GOOGL', 'BTC/USD', 'ETH/USD'])
    
    if st.button('開始回測'):
        with st.spinner('執行回測中...'):
            # 顯示回測結果
            st.success('回測完成！')
            
            # 回測績效指標
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="總收益率", value="25.8%")
            with col2:
                st.metric(label="夏普比率", value="2.1")
            with col3:
                st.metric(label="最大回撤", value="-12.3%")
            with col4:
                st.metric(label="勝率", value="65%")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        st.error(f'發生錯誤: {str(e)}')