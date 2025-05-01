from fastapi import APIRouter, HTTPException
from model import User
from service import user as user_service

router = APIRouter()

@router.post("/create", response_model=User)
def create_user(user: User):
    existing_user = user_service.get_user(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(user)

@router.get("", response_model=User)
def get_user(email: str):
    user = user_service.get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
