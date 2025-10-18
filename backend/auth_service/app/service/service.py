import httpx
import os
from fastapi import HTTPException
from ..models.model import User, Token
from ..security import create_access_token, decode_token
from datetime import timedelta

USER_API_URL = os.environ.get("https://tcc-user-db-530d29de8ef0.herokuapp.com/", "http://localhost:8000/users")

async def login_user(user: User):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_API_URL}/user/email/{user.email}")
            if response.status_code == 404:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            db_user = response.json()

            if user.password != db_user["password"]:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
            return Token(access_token=access_token)
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Could not connect to User Service")

async def get_current_user(token: str):
    email = decode_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_API_URL}/user/email/{email}")
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")

            user_data = response.json()
            return User(id=user_data["id"], name=user_data["name"], email=user_data["email"], cpf=user_data.get('cpf'), password="")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Could not connect to User Service")