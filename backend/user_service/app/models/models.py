from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    password: str
    cpf: str  # Campo que pode conter CPF ou CNPJ

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
    