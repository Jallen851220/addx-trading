import sqlite3
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TradeRecord(Base):
    __tablename__ = 'trade_records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String)
    action = Column(String)  # BUY/SELL
    price = Column(Float)
    quantity = Column(Float)
    total_value = Column(Float)
    strategy = Column(String)
    profit_loss = Column(Float)

class UserSettings(Base):
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)
    risk_tolerance = Column(Float)
    preferred_strategy = Column(String)
    initial_capital = Column(Float)
    notification_settings = Column(String)

class DatabaseManager:
    def __init__(self, db_url='sqlite:///trading_system.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_trade(self, trade_data):
        trade = TradeRecord(**trade_data)
        self.session.add(trade)
        self.session.commit()
    
    def get_trade_history(self, symbol=None, start_date=None, end_date=None):
        query = self.session.query(TradeRecord)
        if symbol:
            query = query.filter(TradeRecord.symbol == symbol)
        if start_date:
            query = query.filter(TradeRecord.timestamp >= start_date)
        if end_date:
            query = query.filter(TradeRecord.timestamp <= end_date)
        return query.all() 