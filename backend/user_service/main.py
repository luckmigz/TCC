

from fastapi import FastAPI 
from app.routes.users import router as user_router

main = FastAPI()

main.include_router(user_router, prefix="/user", tags=["Users"])