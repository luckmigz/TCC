from fastapi import HTTPException
from app.models.model import User, Token
from app.security import get_password_hash, verify_password, create_access_token, decode_token
from datetime import timedelta

# Mock DB em memória
mock_user_db = {}

async def register_user(user: User):
    if user.email in mock_user_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user.id = len(mock_user_db) + 1
    mock_user_db[user.email] = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
    }
    return {"message": "User registered successfully"}

async def login_user(user: User):
    db_user = mock_user_db.get(user.email)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
    return Token(access_token=access_token)

async def get_current_user(token: str):
    email = decode_token(token)
    if email is None or email not in mock_user_db:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_data = mock_user_db[email]
    return User(id=user_data["id"], name=user_data["name"], email=user_data["email"], password="")
