import firebase_admin
from firebase_admin import credentials, auth
import jwt
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
from auth_config import FIREBASE_CONFIG, AUTH_CONFIG
import aioredis
import json

class CloudAuthSystem:
    def __init__(self):
        # 初始化 Firebase
        try:
            cred = credentials.Certificate(FIREBASE_CONFIG)
            self.firebase_app = firebase_admin.initialize_app(cred)
        except ValueError:
            self.firebase_app = firebase_admin.get_app()
            
        # 初始化 Redis 連接
        self.redis = aioredis.from_url(
            AUTH_CONFIG.get('redis_url', 'redis://localhost:6379/0')
        )
        
        # 設置日誌
        self.logger = logging.getLogger(__name__)
    
    async def handle_social_login(self, provider: str) -> Optional[Dict[str, Any]]:
        """處理社交媒體登入"""
        try:
            if provider not in AUTH_CONFIG['oauth2_providers']:
                raise ValueError(f"Unsupported provider: {provider}")
                
            provider_config = AUTH_CONFIG['oauth2_providers'][provider]
            if not provider_config['enabled']:
                raise ValueError(f"{provider} login is disabled")
                
            # 這裡實現具體的社交媒體登入邏輯
            # 返回用戶信息和訪問令牌
            return {
                'provider': provider,
                'user_info': {
                    'display_name': 'Test User',
                    'email': 'test@example.com',
                    'photo_url': None
                },
                'access_token': 'sample_token'
            }
            
        except Exception as e:
            self.logger.error(f"Social login failed: {str(e)}")
            return None
    
    async def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """驗證會話"""
        try:
            session_data = await self.redis.get(f"session:{session_id}")
            if not session_data:
                return None
                
            session = json.loads(session_data)
            if datetime.fromisoformat(session['expires']) < datetime.now():
                await self.redis.delete(f"session:{session_id}")
                return None
                
            return session
            
        except Exception as e:
            self.logger.error(f"Session verification failed: {str(e)}")
            return None
    
    async def create_session(self, user_data: Dict[str, Any]) -> Optional[str]:
        """創建新會話"""
        try:
            session_id = jwt.encode(
                {
                    'user_id': user_data['user_id'],
                    'exp': datetime.utcnow() + AUTH_CONFIG['session_lifetime']
                },
                FIREBASE_CONFIG['apiKey'],
                algorithm='HS256'
            )
            
            session_data = {
                'user_id': user_data['user_id'],
                'created_at': datetime.now().isoformat(),
                'expires': (datetime.now() + AUTH_CONFIG['session_lifetime']).isoformat(),
                'user_data': user_data
            }
            
            await self.redis.set(
                f"session:{session_id}",
                json.dumps(session_data),
                ex=int(AUTH_CONFIG['session_lifetime'].total_seconds())
            )
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Session creation failed: {str(e)}")
            return None
    
    async def revoke_session(self, session_id: str) -> bool:
        """撤銷會話"""
        try:
            await self.redis.delete(f"session:{session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Session revocation failed: {str(e)}")
            return False
    
    async def check_rate_limit(self, user_id: str, action: str) -> bool:
        """檢查速率限制"""
        try:
            key = f"rate_limit:{action}:{user_id}"
            count = await self.redis.incr(key)
            
            if count == 1:
                await self.redis.expire(
                    key,
                    int(AUTH_CONFIG['security']['rate_limit']['window'].total_seconds())
                )
            
            return count <= AUTH_CONFIG['security']['rate_limit']['max_attempts']
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            return False
    
    def close(self):
        """關閉連接"""
        try:
            self.redis.close()
        except Exception as e:
            self.logger.error(f"Connection closure failed: {str(e)}")