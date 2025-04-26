from fastapi import FastAPI
from routes.user_routes import router as user_router 
from routes.restaurant_routes import router as restaurant_router 

app = FastAPI()

app.include_router(user_router, prefix="/user", tags=["Users"]) 
app.include_router(restaurant_router, prefix="/restaurant", tags=["Restaurants"])
