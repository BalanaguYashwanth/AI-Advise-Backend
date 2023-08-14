from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from helpers import getULID


class Message_Item(Base):
    __tablename__ = "message_item"
    id = Column(Integer, primary_key=True)
    user = Column(Text)
    chatgpt = Column(Text)
    bard = Column(Text)
    # Useful for analytics at whattime messages are created
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    # Useful for analytics at when we setup edit feature
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    recent_title_id = Column(String, ForeignKey("recent_title.id"))
    recent_title = relationship("Recent_Title")


class Recent_Title(Base):
    __tablename__ = "recent_title"
    id = Column(String, primary_key=True, index=True, default=getULID)
    uid = Column(String, nullable=False)
    title = Column(String(255), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
