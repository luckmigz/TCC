from fastapi import APIRouter, HTTPException
from service import RestaurantService as restaurant_service

router = APIRouter()

@router.post("/create", response_model=dict, status_code=201)
def create(restaurant: dict):
    existing_restaurant = restaurant_service.get(restaurant["name"])
    if existing_restaurant:
        raise HTTPException(status_code=400, detail="Restaurant already exists")
    return restaurant_service.create_restaurant(restaurant)

@router.get("", response_model=dict, status_code=200)
def get(name: str):
    restaurant = restaurant_service.get(name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.post("/{name}", response_model=dict, status_code=200)
def update(name: str, restaurant: dict):
    existing_restaurant = restaurant_service.get(name)
    if not existing_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant_service.update_restaurant(name, restaurant)