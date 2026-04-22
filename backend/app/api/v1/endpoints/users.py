from fastapi import APIRouter, Depends, HTTPException
from app.database import db_dependency
from sqlalchemy import select
from app.models.users import User
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from pwdlib import PasswordHash
from starlette import status

router = APIRouter()

def hash_password(password: str):
    argon2 = PasswordHash.recommended() #argon2 is hash password algorithm
    return argon2.hash(password)

#CRUD - Create
@router.post("/users/create", response_model=UserResponse)
async def create_user(user: UserCreate, db: db_dependency):
    new_user = User(
        username=user.username,
        password=hash_password(user.password),
        email=user.email,
        phone_number=user.phone_number,
        address=user.address,
        department=user.department,
        role=user.role
    )
    db.add(new_user) #add to database
    db.commit()
    db.refresh(new_user) #refresh to get the new user from database after commit
    return new_user

#CRUD - Read
@router.get("/users")
async def get_users_all(db: db_dependency):
    result = db.execute(select(User))
    users = result.scalars().all()
    return {"users": users}

#CRUD - Read by ID
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_id(user_id: int, db: db_dependency):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

#CRUD - Update by ID
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: db_dependency):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.username = user_update.username
    user.role = user_update.role
    user.email = user_update.email
    user.phone_number = user_update.phone_number
    user.address = user_update.address
    user.department = user_update.department

    if user_update.password:
        user.password = hash_password(user_update.password)

    db.commit()
    db.refresh(user)
    return user 

#CRUD - Delete by ID
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: db_dependency):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": f"User ID:{user_id} deleted successfully"}
