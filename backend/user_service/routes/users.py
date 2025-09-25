from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from ..models.models import User, Restaurant
from ..service.service import (
    create_user, 
    get_user_email, 
    get_user_cpf, 
    update_user, 
    delete_user,
    create_restaurant,
    get_restaurant_cnpj,
    update_restaurant,
    delete_restaurant,
    update_restaurant_occupancy
)

router = APIRouter()

@router.post("/user/create", response_model=Dict, tags=["Users"], status_code=201)
async def create_user_route(user: User):
    """
    Cria um novo usuário (pessoa física ou jurídica).
    """
    try:
        new_user = await create_user(user)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/email/{email}", response_model=User, tags=["Users"])
async def get_user_by_email_route(email: str):
    """
    Busca um usuário pelo email.
    """
    try:
        user = await get_user_email(email)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/user/cpf/{cpf}", response_model=User, tags=["Users"])
async def get_user_by_cpf_route(cpf: str):
    """
    Busca um usuário pelo CPF ou CNPJ.
    """
    try:
        user = await get_user_cpf(cpf)
        print( user )
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/user/update", response_model=Dict, tags=["Users"])
async def update_user_route(user: User):
    """
    Atualiza os dados de um usuário.
    """
    try:
        updated_user = await update_user(user)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/user/delete/{email}", response_model=Dict, tags=["Users"])
async def delete_user_route(email: str):
    """
    Deleta um usuário pelo email.
    """
    try:
        result = await delete_user(email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ===============================
# ROTAS PARA RESTAURANTES
# ===============================

@router.post("/restaurant/create", response_model=Dict, tags=["Restaurants"], status_code=201)
async def create_restaurant_route(restaurant: Restaurant):
    """
    Cria um novo restaurante.
    """
    try:
        new_restaurant = await create_restaurant(restaurant)
        return new_restaurant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/restaurant/{cnpj}", response_model=Dict, tags=["Restaurants"])
async def get_restaurant_by_cnpj_route(cnpj: str):
    """
    Busca um restaurante pelo CNPJ.
    """
    try:
        restaurant = await get_restaurant_cnpj(cnpj)
        return restaurant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/restaurant/update", response_model=Dict, tags=["Restaurants"])
async def update_restaurant_route(restaurant: Restaurant):
    """
    Atualiza os dados de um restaurante.
    """
    try:
        updated_restaurant = await update_restaurant(restaurant)
        return updated_restaurant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/restaurant/delete/{cnpj}", response_model=Dict, tags=["Restaurants"])
async def delete_restaurant_route(cnpj: str):
    """
    Deleta um restaurante pelo CNPJ.
    """
    try:
        result = await delete_restaurant(cnpj)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/restaurant/occupancy/{cnpj}", response_model=Dict, tags=["Restaurants"])
async def update_occupancy_route(cnpj: str, occupancy_update: Dict[str, int]):
    """
    Atualiza a ocupação de um restaurante.
    Exemplo de body: {"new_occupancy": 50}
    """
    try:
        new_occupancy = occupancy_update.get("new_occupancy")
        if new_occupancy is None:
            raise HTTPException(status_code=400, detail="O campo 'new_occupancy' é obrigatório.")
        
        updated_restaurant = await update_restaurant_occupancy(cnpj, new_occupancy)
        return updated_restaurant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

