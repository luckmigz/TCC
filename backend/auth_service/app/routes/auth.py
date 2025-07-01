from fastapi import APIRouter, Header
from app.models.model import User, Token
from app.service import service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user: User):
    return await service.register_user(user)

@router.post("/login", response_model=Token)
async def login(user: User):
    return await service.login_user(user)

@router.get("/me")
async def get_me(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Espera header: Authorization: Bearer <token>
    return await service.get_current_user(token)
