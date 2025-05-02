from fastapi import APIRouter, Body, HTTPException, Path
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

@router.post("/{cnpj}", response_model=dict, status_code=200)
def update(cnpj: str, restaurant: dict):
    existing_restaurant = restaurant_service.get(cnpj)
    if not existing_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant_service.update_restaurant(cnpj, restaurant)

@router.patch("/{cnpj}/occupancy", response_model=dict, status_code=200)
def update_occupancy_route(
    cnpj: str = Path(..., description="CNPJ do restaurante"),
    occupancy: int = Body(..., embed=True)
):
    try:
        updated = restaurant_service.update_occupancy(cnpj, occupancy)
        if not updated:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))