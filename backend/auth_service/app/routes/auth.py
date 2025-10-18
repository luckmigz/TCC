from fastapi import APIRouter, HTTPException, Header

from backend.auth_service.app.security.security import decode_token
from ..models.model import LoginRequest, Token
from ..service import service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest):
   if credentials.login_as == 'restaurant':   
        return await service.login_restaurant(
            email=credentials.email,
            password=credentials.password
        )
   else:
        return await service.login_user(
            email=credentials.email,
            password=credentials.password
        )

@router.get("/me")
async def get_me(authorization: str = Header(...)):
    try:
        token_type, token = authorization.split(" ")
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    token_scope = payload.get("scope")

    if token_scope == "restaurant":
        return await service.get_current_restaurant(token)
    elif token_scope == "user":
        return await service.get_current_user(token)
    else:
        # Caso o token não tenha o escopo esperado
        raise HTTPException(status_code=401, detail="Invalid token scope")