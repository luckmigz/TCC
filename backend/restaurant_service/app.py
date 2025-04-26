from fastapi import FastAPI
from routes.restaurants import router as restaurant_router

app = FastAPI()

app.include_router(restaurant_router, prefix="/restaurant", tags=["Restaurants"])