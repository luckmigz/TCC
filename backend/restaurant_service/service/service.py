import json 
from pathlib import Path
from typing import List, Optional
from models.model import Restaurant

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
    def create(cls,restaurant: Restaurant) -> Restaurant:
        restaurants = cls._load_restaurants()
        max_id = max((r.id for r in restaurants if r.id is not None), default=0)
        restaurant.id = max_id + 1
        restaurants.append(restaurant)
        cls._save_restaurants(restaurants)
        return restaurant

    @classmethod
    def get(cls,name: str) -> Optional[Restaurant]:
        return next((restaurant for restaurant in cls._load_restaurants() if restaurant.id == id), None)

    @classmethod
    def update(cls,updated: Restaurant) -> Optional[Restaurant]:
        restaurants = cls._load_restaurants()
        for i, restaurant in enumerate(restaurants):
            if restaurant.id == updated.id:
                restaurants[i] = updated
                cls._save_restaurants(restaurants)
                return updated
        return None