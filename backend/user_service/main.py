import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from fastapi import FastAPI 
from app.routes.users import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/user", tags=["Users"])