from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.models.users import User
from app.database import engine, Base
from app.api.v1.api import api_router
from app.api.v1.endpoints.auth import get_current_user
from app.middleware.cors import add_cors_middleware
from app.middleware.logging import ProcessTimeMiddleware

#Setup คำสั่งที่ต้องทำงานตลอดการ run
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MySQL and creating tables...")
    Base.metadata.create_all(bind=engine) #update table ใน database ตาม model ที่สร้างไว้ 
    yield
    print("Shutting down application and cleaning up...")

app = FastAPI(lifespan=lifespan)

add_cors_middleware(app)
app.add_middleware(ProcessTimeMiddleware)

app.include_router(api_router, prefix="/api/v1")

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

@app.get("/me")
async def read_current_user(current_user: Annotated[dict, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return current_user