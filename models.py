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

    title_id = Column(String, ForeignKey("recent_title.id"))
    title = relationship("Recent_Title")


class Recent_Title(Base):
    __tablename__ = "recent_title"
    # need to use UUID
   
    id = Column(String,primary_key=True, index=True,default=getULID)
    uid = Column(String, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    # section_id = Column(Integer, ForeignKey("section.id"))
    # section = relationship("Section")

# class Section(Base):
#     __tablename__ = "section"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(255), nullable=False)

#     user_id = Column(Integer,ForeignKey('user.id'))
#     user = relationship('User')

# class User(Base):
#     __tablename__ = "user"
#     id = Column(Integer, primary_key=True)
#     uid = Column(String)
#     name = Column(String)
#     email = Column(String)
#     time_created = Column(DateTime(timezone=True), server_default=func.now())
