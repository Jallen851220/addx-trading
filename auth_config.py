import os
from datetime import timedelta

# Firebase 配置
FIREBASE_CONFIG = {
    'apiKey': "AIzaSyADDX_trading_system",
    'authDomain': "addx-trading.firebaseapp.com",
    'projectId': "addx-trading",
    'storageBucket': "addx-trading.appspot.com",
    'messagingSenderId': "123456789",
    'appId': "1:123456789:web:abcdef",
    'databaseURL': "https://addx-trading.firebaseio.com"
}

# 認證設置
AUTH_CONFIG = {
    'session_lifetime': timedelta(days=7),
    'login_attempts_limit': 5,
    'login_timeout': timedelta(minutes=30),
    'password_min_length': 8,
    'require_email_verification': True,
    
    # OAuth2 提供者設置
    'oauth2_providers': {
        'google': {
            'enabled': True,
            'scopes': ['email', 'profile']
        },
        'line': {
            'enabled': True,
            'scopes': ['profile', 'openid', 'email']
        },
        'telegram': {
            'enabled': True
        }
    },
    
    # 安全設置
    'security': {
        'enable_2fa': True,
        'jwt_expiry': timedelta(hours=24),
        'refresh_token_expiry': timedelta(days=30),
        'password_hash_rounds': 12,
        'rate_limit': {
            'enabled': True,
            'max_attempts': 100,
            'window': timedelta(minutes=15)
        }
    }
}

# 數據庫設置
DB_CONFIG = {
    'url': 'sqlite:///trading_system.db',
    'pool_size': 20,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 1800
}

# Redis 設置 (用於會話管理和緩存)
REDIS_CONFIG = {
    'url': 'redis://localhost:6379/0',
    'max_connections': 20,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True
}

# 日誌設置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'trading_system.log',
            'mode': 'a'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
} 