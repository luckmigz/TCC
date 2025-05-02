from pydantic import BaseModel 
from typing import Optional 

class Restaurant(BaseModel):
    id: Optional[int] = None
    name: str 
    address: str | None = None
    cep: str
    cnpj: str
    phone_number: str 
    cuisine_type: str 
    rating: Optional[float] 
    is_open: bool 
    occupancy: int 
    max_occupancy: int
    
    class Config: 
        orm_mode = True # Permite que o Pydantic saiba como lidar com objetos ORM (se necessário)
    

