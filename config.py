CONFIG = {
    'database': {
        'url': 'sqlite:///trading_system.db'
    },
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender': 'your_email@gmail.com',
        'password': 'your_app_password',
        'recipient': 'recipient@email.com'
    },
    'telegram': {
        'enabled': True,
        'bot_token': 'your_bot_token',
        'chat_id': 'your_chat_id'
    },
    'line': {
        'enabled': True,
        'channel_access_token': 'your_line_token',
        'user_id': 'your_line_user_id'
    },
    'trading': {
        'initial_capital': 100000,
        'risk_per_trade': 0.02,
        'default_symbols': [
            'AAPL', 'GOOGL', 'TSLA',  # 股票
            'BTC/USDT', 'ETH/USDT',   # 加密貨幣
            'GC=F', 'SI=F'            # 期貨
        ]
    }
} 