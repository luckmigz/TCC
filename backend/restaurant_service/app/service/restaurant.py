import json 
from pathlib import Path
from typing import List, Optional
from models import Restaurant
import httpx 

async def fetch_cep(cep: str) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
            response.raise_for_status()
            data = response.json()
            return f"{data['logradouro']}, {data['bairro']}, {data['localidade']}-{data['uf']}"
        except httpx.RequestError as e:
            print(f"An error occurred while fetching coordinates: {e}")
            return None
    




class RestaurantService:
    
    DB_PATH = Path("backend/restaurant_service/app/restaurants.json")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _load_restaurants(cls) -> List[Restaurant]:
        if not cls.DB_PATH.exists():
            return []

        with cls.DB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return [Restaurant(**restaurant) for restaurant in data]
    @classmethod
    def _save_restaurants(cls,restaurants: List[Restaurant]):
        with cls.DB_PATH.open("w", encoding="utf-8") as f:
            json.dump([restaurant.dict() for restaurant in restaurants], f, ensure_ascii=False, indent=4)
            
    @classmethod
    async def create(cls,restaurant: Restaurant) -> Restaurant:
        restaurants = await cls._load_restaurants()
        max_id = max((r.id for r in restaurants if r.id is not None), default=0)
        restaurant.id = max_id + 1
        restaurant.address = await fetch_cep(restaurant.cep)
        if restaurant.address is None:
            raise ValueError("Invalid CEP or unable to fetch address.")
        restaurants.append(restaurant)
        cls._save_restaurants(restaurants)
        return restaurant

    @classmethod
    def get(cls,name: str) -> Optional[Restaurant]:
        return next((restaurant for restaurant in cls._load_restaurants() if restaurant.id == id), None)

    @classmethod
    async def update(cls,updated: Restaurant, cnpj:str) -> Optional[Restaurant]:
        restaurants =  await cls._load_restaurants()
        for i, r in enumerate(restaurants):
            if r.cnpj == cnpj:
                updated.id = r.id
                updated.address = await fetch_cep(updated.cep)
                restaurants[i] = updated
                cls._save_restaurants(restaurants)
            return updated
        return None
    
    @classmethod
    def update_occupancy(cls, cnpj: str, occupancy: int) -> Optional[Restaurant]:
        restaurants = cls._load_restaurants()
        for i, r in enumerate(restaurants):
            if r.cnpj == cnpj:
                if not r.is_open:
                    raise ValueError("Restaurant is closed.")
                if occupancy > r.max_occupancy:
                    raise ValueError("Occupancy exceeds maximum limit.")
                r.occupancy = occupancy
                restaurants[i] = r
                cls._save_restaurants(restaurants)
                return r
        return None