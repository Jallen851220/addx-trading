import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime

class NotificationSystem:
    def __init__(self, config):
        self.email_config = config.get('email', {})
        self.telegram_config = config.get('telegram', {})
        self.line_config = config.get('line', {})
        
    def send_email_alert(self, subject, message):
        """發送電子郵件通知"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
    
    def send_telegram_alert(self, message):
        """發送Telegram通知"""
        try:
            bot_token = self.telegram_config['bot_token']
            chat_id = self.telegram_config['chat_id']
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram notification failed: {str(e)}")
            return False
    
    def send_line_alert(self, message):
        """發送LINE通知"""
        try:
            headers = {
                'Authorization': f'Bearer {self.line_config["channel_access_token"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'to': self.line_config['user_id'],
                'messages':[{
                    'type': 'text',
                    'text': message
                }]
            }
            
            response = requests.post(
                'https://api.line.me/v2/bot/message/push',
                headers=headers,
                data=json.dumps(data)
            )
            return response.status_code == 200
        except Exception as e:
            print(f"LINE notification failed: {str(e)}")
            return False
    
    def send_trade_alert(self, trade_data):
        """發送交易相關通知"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
交易提醒 - {timestamp}
商品: {trade_data['symbol']}
操作: {trade_data['action']}
價格: {trade_data['price']}
數量: {trade_data['quantity']}
總值: {trade_data['total_value']}
理由: {trade_data['reason']}
        """
        
        # 根據用戶設置發送不同類型的通知
        if self.email_config.get('enabled', False):
            self.send_email_alert("交易提醒", message)
        
        if self.telegram_config.get('enabled', False):
            self.send_telegram_alert(message)
            
        if self.line_config.get('enabled', False):
            self.send_line_alert(message) 