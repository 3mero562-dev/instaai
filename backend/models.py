from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Instagram Integration
    instagram_page_id = Column(String, unique=True, index=True, nullable=True)
    instagram_access_token = Column(String, nullable=True)
    
    # AI & Bot Control Settings
    business_description = Column(Text, nullable=True)
    ai_instructions = Column(Text, nullable=True)
    bot_status = Column(String, default="disabled") # enabled, disabled, paused, human_takeover

    # Relationships
    products = relationship("Product", back_populates="owner", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="owner", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="owner", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="products")

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="faqs")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_ig_id = Column(String, index=True, nullable=False)
    details = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="orders")