from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class BotSettingsUpdate(BaseModel):
    business_description: Optional[str] = None
    ai_instructions: Optional[str] = None
    bot_status: Optional[str] = None  # enabled, disabled, paused, human_takeover
    instagram_page_id: Optional[str] = None
    instagram_access_token: Optional[str] = None

class UserResponse(UserBase):
    id: int
    instagram_page_id: Optional[str] = None
    bot_status: str
    business_description: Optional[str] = None
    ai_instructions: Optional[str] = None

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# FAQ Schemas
class FAQBase(BaseModel):
    question: str
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQResponse(FAQBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Order Schemas
class OrderResponse(BaseModel):
    id: int
    customer_ig_id: str
    details: str
    status: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True