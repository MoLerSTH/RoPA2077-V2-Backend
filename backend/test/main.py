import hashlib

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import test.models as models
import test.schemas as schemas
from test.database import SessionLocal, init_db

app = FastAPI()

init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/register", response_model=schemas.UserResponse)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User)
        .filter(
            (models.User.username == user_in.username) | (models.User.email == user_in.email)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login")
def login(login_request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == login_request.username)
        .first()
    )
    if not user or not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Login successful", "username": user.username}
