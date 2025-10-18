from fastapi import APIRouter, Header
from ..models.model import User, Token
from ..service import service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(user: User):
    if "cnpj" in user.email:
        return await service.login_restaurant(user)
    return await service.login_user(user)

@router.get("/me")
async def get_me(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    if "cnpj" in token:
        return await service.get_current_restaurant(token)
    return await service.get_current_user(token)