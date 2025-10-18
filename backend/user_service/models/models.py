from pydantic import BaseModel, EmailStr
from typing import Optional, Union

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    password: str
    cpf: str  # Campo que pode conter CPF (pessoa física) ou CNPJ (pessoa jurídica/restaurante)

class Restaurant(BaseModel):
    id: Optional[str] = None
    name: str 
<<<<<<< HEAD
=======
    email: EmailStr
    password: str
>>>>>>> 129ae5b9cf1ad1a82edd2e37307d386e91aad25e
    address: Optional[str] = None
    cep: str
    cnpj: str
    phone_number: str 
    cuisine_type: str 
    rating: Optional[float] = None
    is_open: bool 
    occupancy: int 
    max_occupancy: int
<<<<<<< HEAD
    
=======
    
>>>>>>> 129ae5b9cf1ad1a82edd2e37307d386e91aad25e
