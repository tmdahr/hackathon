# app/models.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), unique=True, index=True)
    money = Column(Integer, default=0)
    pollution_level = Column(Integer, default=80) # 초기 오염도 80
    rod_level = Column(Integer, default=1)        # 낚싯대 레벨 1
    
    # 낚시 기록(도감)과 연결
    collections = relationship("Collection", back_populates="user")

class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    type = Column(Integer) # 0:쓰레기, 1:교란종, 2:일반, 3:멸종위기
    price = Column(Integer)
    image_url = Column(String(255))
    
    collections = relationship("Collection", back_populates="species")

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    species_id = Column(Integer, ForeignKey("species.id"))
    caught_count = Column(Integer, default=0)
    is_new = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="collections")
    species = relationship("Species", back_populates="collections")