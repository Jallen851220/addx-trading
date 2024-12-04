import sqlite3
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TradeRecord(Base):
    __tablename__ = 'trade_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, index=True)
    symbol = Column(String)
    action = Column(String)  # BUY/SELL
    price = Column(Float)
    quantity = Column(Float)
    total_value = Column(Float)
    strategy = Column(String)
    profit_loss = Column(Float)
    status = Column(String)  # OPEN/CLOSED
    
class UserSettings(Base):
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)
    risk_tolerance = Column(Float)
    preferred_strategy = Column(String)
    initial_capital = Column(Float)
    notification_settings = Column(JSON)
    trading_pairs = Column(JSON)
    auto_trading = Column(JSON)

class PortfolioSnapshot(Base):
    __tablename__ = 'portfolio_snapshots'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_value = Column(Float)
    cash_balance = Column(Float)
    positions = Column(JSON)
    metrics = Column(JSON)

class DatabaseManager:
    def __init__(self, db_url='sqlite:///trading_system.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    async def save_trade(self, trade_data):
        """保存交易記錄"""
        try:
            trade = TradeRecord(**trade_data)
            self.session.add(trade)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error saving trade: {e}")
            return False
    
    async def get_trade_history(self, user_id, symbol=None, start_date=None, end_date=None):
        """獲取交易歷史"""
        query = self.session.query(TradeRecord).filter(TradeRecord.user_id == user_id)
        
        if symbol:
            query = query.filter(TradeRecord.symbol == symbol)
        if start_date:
            query = query.filter(TradeRecord.timestamp >= start_date)
        if end_date:
            query = query.filter(TradeRecord.timestamp <= end_date)
            
        return query.all()
    
    async def save_portfolio_snapshot(self, snapshot_data):
        """保存投資組合快照"""
        try:
            snapshot = PortfolioSnapshot(**snapshot_data)
            self.session.add(snapshot)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error saving portfolio snapshot: {e}")
            return False
    
    async def get_user_settings(self, user_id):
        """獲取用戶設置"""
        return self.session.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
    
    async def update_user_settings(self, user_id, settings_data):
        """更新用戶設置"""
        try:
            settings = self.session.query(UserSettings).filter(
                UserSettings.user_id == user_id
            ).first()
            
            if settings:
                for key, value in settings_data.items():
                    setattr(settings, key, value)
            else:
                settings = UserSettings(user_id=user_id, **settings_data)
                self.session.add(settings)
                
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error updating user settings: {e}")
            return False
    
    async def get_portfolio_history(self, user_id, start_date=None, end_date=None):
        """獲取投資組合歷史數據"""
        query = self.session.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.user_id == user_id
        )
        
        if start_date:
            query = query.filter(PortfolioSnapshot.timestamp >= start_date)
        if end_date:
            query = query.filter(PortfolioSnapshot.timestamp <= end_date)
            
        return query.order_by(PortfolioSnapshot.timestamp).all()
    
    def close(self):
        """關閉數據庫連接"""
        self.session.close()