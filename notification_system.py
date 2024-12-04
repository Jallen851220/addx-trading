import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime
import asyncio
import aiohttp
from typing import Dict, Any, List

class NotificationSystem:
    def __init__(self):
        self.notification_queue = asyncio.Queue()
        self.notification_history = []
        
    async def send_notification(self, user_id: str, message: Dict[str, Any], channels: List[str]):
        """發送通知到指定渠道"""
        try:
            # 添加時間戳和用戶ID
            notification = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'message': message,
                'channels': channels
            }
            
            # 將通知加入隊列
            await self.notification_queue.put(notification)
            
            # 處理通知
            tasks = []
            for channel in channels:
                if channel == 'email':
                    tasks.append(self.send_email_notification(notification))
                elif channel == 'telegram':
                    tasks.append(self.send_telegram_notification(notification))
                elif channel == 'line':
                    tasks.append(self.send_line_notification(notification))
                    
            # 並行發送所有通知
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 記錄通知歷史
            self.notification_history.append({
                **notification,
                'status': 'success' if all(r is not None for r in results) else 'partial_failure',
                'results': results
            })
            
            return True
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False
    
    async def send_email_notification(self, notification: Dict[str, Any]):
        """發送電子郵件通知"""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = notification['message'].get('subject', 'ADDX 交易提醒')
            msg['From'] = "noreply@addx-trading.com"
            msg['To'] = notification['message'].get('email')
            
            # 創建HTML內容
            html_content = f"""
            <html>
                <body>
                    <h2>{notification['message'].get('title', '交易提醒')}</h2>
                    <p>{notification['message'].get('content')}</p>
                    <hr>
                    <p style="color: gray; font-size: 12px;">
                        發送時間: {notification['timestamp']}
                    </p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # 使用異步方式發送郵件
            async with aiohttp.ClientSession() as session:
                # 這裡應該使用您的郵件服務API
                pass
                
            return True
        except Exception as e:
            print(f"Email notification failed: {str(e)}")
            return False
    
    async def send_telegram_notification(self, notification: Dict[str, Any]):
        """發送Telegram通知"""
        try:
            message_text = f"""
🔔 *{notification['message'].get('title', '交易提醒')}*

{notification['message'].get('content')}

_發送時間: {notification['timestamp']}_
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api.telegram.org/bot{notification['bot_token']}/sendMessage",
                    json={
                        "chat_id": notification['message'].get('telegram_chat_id'),
                        "text": message_text,
                        "parse_mode": "Markdown"
                    }
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            print(f"Telegram notification failed: {str(e)}")
            return False
    
    async def send_line_notification(self, notification: Dict[str, Any]):
        """發送LINE通知"""
        try:
            message = {
                'type': 'flex',
                'altText': notification['message'].get('title', '交易提醒'),
                'contents': {
                    'type': 'bubble',
                    'body': {
                        'type': 'box',
                        'layout': 'vertical',
                        'contents': [
                            {
                                'type': 'text',
                                'text': notification['message'].get('title', '交易提醒'),
                                'weight': 'bold',
                                'size': 'xl'
                            },
                            {
                                'type': 'text',
                                'text': notification['message'].get('content'),
                                'wrap': True,
                                'margin': 'md'
                            }
                        ]
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.line.me/v2/bot/message/push',
                    headers={
                        'Authorization': f"Bearer {notification['line_token']}",
                        'Content-Type': 'application/json'
                    },
                    json={
                        'to': notification['message'].get('line_user_id'),
                        'messages': [message]
                    }
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            print(f"LINE notification failed: {str(e)}")
            return False
    
    async def get_notification_history(self, user_id: str, limit: int = 50):
        """獲取通知歷史"""
        return [n for n in self.notification_history if n['user_id'] == user_id][-limit:]
    
    async def clear_notification_history(self, user_id: str):
        """清除通知歷史"""
        self.notification_history = [n for n in self.notification_history if n['user_id'] != user_id] 