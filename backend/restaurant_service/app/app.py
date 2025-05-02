from fastapi import FastAPI
import uvicorn
from routes.restaurants import router as restaurant_router

app = FastAPI()

app.include_router(restaurant_router, prefix="/restaurant", tags=["Restaurants"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0" , port=8001, reload=True)