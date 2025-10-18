from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    password: str
    cpf: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None


class Restaurant(BaseModel):
    id: Optional[str] = None
    name: str 
    email: EmailStr
    password: str
    address: Optional[str] = None
    cep: str
    cnpj: str
    phone_number: str 
    cuisine_type: str 
    rating: Optional[float] = None
    is_open: bool 
    occupancy: int 
    max_occupancy: int

    class Config:
        from_attributes = True 
        

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    login_as: Literal['user', 'restaurant'] = 'user'