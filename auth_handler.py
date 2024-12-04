from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from datetime import datetime
import jwt
from typing import Optional
import redis
from auth_config import AUTH_CONFIG
from database_handler import DatabaseManager
import requests

class AuthenticationSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.redis_client = redis.from_url(AUTH_CONFIG['session_config']['redis_url'])
        
    async def create_jwt_token(self, user_data: dict) -> str:
        """創建 JWT Token"""
        payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'exp': datetime.utcnow() + AUTH_CONFIG['jwt_expiry']
        }
        return jwt.encode(
            payload,
            AUTH_CONFIG['jwt_secret'],
            algorithm=AUTH_CONFIG['jwt_algorithm']
        )
    
    async def verify_jwt_token(self, token: str) -> Optional[dict]:
        """驗證 JWT Token"""
        try:
            payload = jwt.decode(
                token,
                AUTH_CONFIG['jwt_secret'],
                algorithms=[AUTH_CONFIG['jwt_algorithm']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def oauth2_google_login(self, code: str):
        """Google OAuth2 登入"""
        google_config = AUTH_CONFIG['oauth2_providers']['google']
        
        # 獲取訪問令牌
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': google_config['client_id'],
            'client_secret': google_config['client_secret'],
            'redirect_uri': google_config['redirect_uri'],
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
            
        access_token = token_response.json()['access_token']
        
        # 獲取用戶信息
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
            
        user_info = user_info_response.json()
        
        # 創建或更新用戶
        user_data = await self.db.create_or_update_user({
            'email': user_info['email'],
            'name': user_info['name'],
            'oauth_provider': 'google',
            'oauth_id': user_info['id']
        })
        
        # 創建 session
        token = await self.create_jwt_token(user_data)
        return {'token': token, 'user': user_data}
    
    async def line_login(self, code: str):
        """LINE 登入"""
        line_config = AUTH_CONFIG['oauth2_providers']['line']
        
        # 獲取訪問令牌
        token_response = requests.post(
            'https://api.line.me/oauth2/v2.1/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': line_config['client_id'],
                'client_secret': line_config['client_secret'],
                'redirect_uri': line_config['redirect_uri']
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get LINE access token")
            
        access_token = token_response.json()['access_token']
        
        # 獲取用戶信息
        profile_response = requests.get(
            'https://api.line.me/v2/profile',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if profile_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get LINE profile")
            
        profile = profile_response.json()
        
        # 創建或更新用戶
        user_data = await self.db.create_or_update_user({
            'line_id': profile['userId'],
            'name': profile['displayName'],
            'oauth_provider': 'line'
        })
        
        token = await self.create_jwt_token(user_data)
        return {'token': token, 'user': user_data}
    
    async def telegram_auth(self, telegram_data: dict):
        """Telegram 認證"""
        # 驗證 Telegram 數據
        if not self._verify_telegram_data(telegram_data):
            raise HTTPException(status_code=400, detail="Invalid Telegram data")
            
        user_data = await self.db.create_or_update_user({
            'telegram_id': telegram_data['id'],
            'name': telegram_data['first_name'],
            'oauth_provider': 'telegram'
        })
        
        token = await self.create_jwt_token(user_data)
        return {'token': token, 'user': user_data}
    
    def _verify_telegram_data(self, data: dict) -> bool:
        """驗證 Telegram 數據的真實性"""
        # 實現 Telegram 數據驗證邏輯
        return True  # 簡化示例 