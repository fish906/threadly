from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz
from .db import Base

user_tz = pytz.timezone("Europe/Berlin")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    key_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="topic")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("Topic", back_populates="messages")
    ip_logs = relationship("IPLog", back_populates="message", cascade="all, delete-orphan")

class IPLog(Base):
    __tablename__ = "ip_logs"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    ip_address = Column(String(45), index=True, nullable=False)  # IPv6 max length = 45
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(user_tz))

    message = relationship("Message", back_populates="ip_logs")