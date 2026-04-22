# app/models/users.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    phone_number = Column(String(20), unique=True)
    address = Column(String(255))
    department = Column(String(255))
    role = Column(String(50))


