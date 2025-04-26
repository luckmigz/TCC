from fastapi import APIRouter, HTTPException
from models import User


router = APIRouter()

mock_users_db = {}

@router.post("/register")
async def register_user(user: User):
    if user.email in mock_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    user.id = len(mock_users_db) + 1
    mock_users_db[user.email] = user
    return {"message": "User registered successfully", "user": user}

@router.get("/login")
async def login_user(user: User):
    stored_user = mock_users_db.get(user.email)
    if not stored_user or stored_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "user": stored_user}