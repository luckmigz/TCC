from fastapi import APIRouter, HTTPException
from models.models import User
from service.service import get_user, set_user 

router = APIRouter()

@router.post("/create", response_model=User)
def create_user(user: User):
    existing_user = get_user(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return set_user(user)

@router.get("", response_model=User)
def get_user(email: str):
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
