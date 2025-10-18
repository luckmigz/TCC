import httpx
import os
from fastapi import HTTPException
from ..models.model import Restaurant, User, Token
from ..security.security import create_access_token, decode_token 
from datetime import timedelta

USER_API_URL = "https://tcc-user-db-530d29de8ef0.herokuapp.com"

async def login_user(user: User):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_API_URL}/user/email/{user.email}")
            print(response)
            print(response.status_code)
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
            return User(name=user_data["name"], email=user_data["email"], cpf=user_data.get('cpf'), password="")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Could not connect to User Service")
        
async def login_restaurant(restaurant: Restaurant):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_API_URL}/restaurant/email/{restaurant.email}")
            print(response)
            print(response.status_code)
            if response.status_code == 404:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            db_user = response.json()

            if restaurant.password != db_user["password"]:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            access_token = create_access_token(data={"sub": restaurant.email}, expires_delta=timedelta(minutes=30))
            return Token(access_token=access_token)
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Could not connect to User Service")

async def get_current_restaurant(token: str):
    email = decode_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_API_URL}/restaurant/email/{email}")
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")

            restaurant_data = response.json()
            return Restaurant(
                name=restaurant_data["name"],
                email=restaurant_data["email"],
                address=restaurant_data.get("address"),
                cep=restaurant_data["cep"],
                cnpj=restaurant_data["cnpj"],
                phone_number=restaurant_data["phone_number"],
                cuisine_type=restaurant_data["cuisine_type"],
                is_open=restaurant_data["is_open"],
                occupancy=restaurant_data["occupancy"],
                max_occupancy=restaurant_data["max_occupancy"],
                password=""
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Could not connect to User Service")