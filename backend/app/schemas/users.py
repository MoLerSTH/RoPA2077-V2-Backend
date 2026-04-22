# app/schemas/users.py
from typing import Optional

from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str
    address: str
    department: str
    role: str

class UserCreate(UserBase): #for registration
    pass

class UserResponse(UserBase): #for frontend
    id: int
    model_config = ConfigDict(from_attributes=True) #connect pydantic to SQLAlchemy model (ORM)

class UserCurrent(BaseModel):
    username: str
    user_id: int
    role: str
    email: str
    phone_number: str
    address: str
    department: str
    
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token:  str
    token_type:    str

class UserUpdate(BaseModel):
    username: str
    email: str
    phone_number: str
    address: str
    department: str
    role: str
    password: Optional[str] = None