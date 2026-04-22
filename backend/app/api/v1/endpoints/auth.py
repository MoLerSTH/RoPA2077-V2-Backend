import jwt
from typing import Annotated
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.users import User
from app.database import db_dependency
from sqlalchemy import select 
from sqlalchemy.orm import Session
from app.schemas.users import LoginRequest, Token, UserCurrent
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def create_access_token(
        username: str, 
        role: str, 
        user_id: int, 
        email: str,
        phone_number: str,
        address: str,
        department: str,
        expires_delta: timedelta
    ) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": username,
        "role": role,
        "email": email,
        "phone_number": phone_number,
        "address": address,
        "user_id": user_id,
        "exp": expire,
        "department": department
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token 

async def get_current_user(token : str = Depends(oauth2_scheme)):
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        user_role: str = payload.get("role")
        user_email: str = payload.get("email")
        phone_number: str = payload.get("phone_number")
        address: str = payload.get("address")
        department: str = payload.get("department")
        if username is None or user_id is None or user_role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        return UserCurrent(
            username=username,
            user_id=user_id,
            role=user_role,
            email=user_email,
            phone_number=phone_number,
            address=address,
            department=department
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    

@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login(
    db: db_dependency,
    login_data: LoginRequest,
):
    # 1. Get user from database by email
    statement = select(User).where(User.email == login_data.email) #prepare SQL statement to select user by email
    user = db.execute(statement).scalar_one_or_none() #use SQL statement to get user from database

    # 2. Verify password
    verify = PasswordHash.recommended().verify(login_data.password, user.password) #verify password by comparing input and hashed password in database
    if not user or not verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    # return {"message": "Login successful", "username": user.username}

    # 3. Create JWT (Access Token)
    token = create_access_token(
        username=user.username,
        role=user.role,
        user_id=user.id,
        email=user.email,
        phone_number=user.phone_number,
        address=user.address,
        department=user.department,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": token, 
            "token_type": "bearer"}

