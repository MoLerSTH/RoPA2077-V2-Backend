# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, controller, processor, dpo, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, tags=["Users"])
api_router.include_router(controller.router, prefix="/ropa", tags=["RoPA Controller"])
api_router.include_router(processor.router, prefix="/ropa", tags=["RoPA Processor"])
api_router.include_router(dpo.router, prefix="/dpo", tags=["DPO"])
api_router.include_router(dashboard.router, prefix="/dashboard",tags=["Dashboard"])