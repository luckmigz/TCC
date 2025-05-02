from fastapi import APIRouter, Body, HTTPException, Path, logger
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
@router.put("/{cnpj}", response_model=Restaurant, status_code=200)
async def update(cnpj: str, restaurant: Restaurant):
    existing_restaurant = restaurant_service.get_by_cnpj(cnpj)
    if not existing_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    updated_restaurant = await restaurant_service.update(restaurant, cnpj)  # Tornando a chamada assíncrona
    return updated_restaurant

# Atualização de ocupação
@router.patch("/{cnpj}/occupancy", response_model=Restaurant, status_code=200)
def update_occupancy(
    cnpj: str = Path(..., description="CNPJ do restaurante"),
    occupancy: int = Body(..., embed=True)
):
    try:
        updated = restaurant_service.update_occupancy(cnpj, occupancy)
        
        if not updated:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        if occupancy > updated.max_occupancy:
            raise HTTPException(status_code=400, detail="Occupancy exceeds maximum limit")
        
        if not updated.is_open:
            print("Restaurant is closed")
            raise HTTPException(status_code=400, detail="Restaurant is closed")
    
        
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Deletar restaurante 
@router.delete("/{cnpj}", status_code=204)
def delete(cnpj: str):
    success = restaurant_service.delete(cnpj)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return None