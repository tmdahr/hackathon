# app/models.py (전체 덮어쓰기)

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), unique=True, index=True)
    money = Column(Integer, default=0)
    pollution_level = Column(Integer, default=80) 
    rod_level = Column(Integer, default=1)        
    
    collections = relationship("Collection", back_populates="user")
    inventory = relationship("Inventory", back_populates="user") # 추가됨

class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    type = Column(Integer) 
    price = Column(Integer)
    image_url = Column(String(255))

    habitat = Column(String(50), default="알 수 없음")
    description = Column(String(1000))
    
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

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer) # 상점 아이템 ID
    
    user = relationship("User", back_populates="inventory")