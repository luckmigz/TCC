from fastapi import APIRouter, Body, HTTPException, Path
from service import RestaurantService as restaurant_service
from models import Restaurant

router = APIRouter()

# Criação do restaurante
@router.post("/create", response_model=Restaurant, status_code=201)
async def create(restaurant: Restaurant):
    existing_restaurant = restaurant_service.get(restaurant.name)
    if existing_restaurant:
        raise HTTPException(status_code=400, detail="Restaurant already exists")
    # Cria o restaurante e retorna uma instância de Restaurant
    created_restaurant = await restaurant_service.create(restaurant.dict())
    return created_restaurant

# Obtenção do restaurante
@router.get("", response_model=Restaurant, status_code=200)
def get(name: str):
    restaurant = restaurant_service.get(name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

# Atualização do restaurante
@router.post("/{cnpj}", response_model=Restaurant, status_code=200)
def update(cnpj: str, restaurant: dict):
    existing_restaurant = restaurant_service.get(cnpj)
    if not existing_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    updated_restaurant = restaurant_service.update(cnpj, restaurant)
    return updated_restaurant

# Atualização de ocupação
@router.patch("/{cnpj}/occupancy", response_model=Restaurant, status_code=200)
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
