from fastapi import APIRouter, HTTPException
from models import Restaruant

router = APIRouter()

mock_restaurants_db = {}


@router.post("/register")
async def register_restaurant(restaurant: Restaruant):
    if restaurant.email in mock_restaurants_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    restaurant.id = len(mock_restaurants_db) + 1
    mock_restaurants_db[restaurant.email] = restaurant
    return {"message": "Restaurant registered successfully", "restaurant": restaurant}

@router.get("/{name}")
async def get_restaurant(name: str):
    restaurant = mock_restaurants_db.get(name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant
