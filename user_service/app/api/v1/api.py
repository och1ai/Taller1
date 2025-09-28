from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, audit

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["audit"])
