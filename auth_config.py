import os
from dotenv import load_dotenv
from datetime import timedelta
import jwt

# 載入環境變數
load_dotenv()

AUTH_CONFIG = {
    'jwt_secret': os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
    'jwt_algorithm': 'HS256',
    'jwt_expiry': timedelta(days=1),
    'oauth2_providers': {
        'google': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
            'scope': ['email', 'profile']
        },
        'line': {
            'client_id': os.getenv('LINE_CLIENT_ID'),
            'client_secret': os.getenv('LINE_CLIENT_SECRET'),
            'redirect_uri': os.getenv('LINE_REDIRECT_URI')
        },
        'telegram': {
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'webhook_url': os.getenv('TELEGRAM_WEBHOOK_URL')
        }
    },
    'session_config': {
        'session_lifetime': timedelta(hours=24),
        'session_type': 'redis',
        'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    }
} 