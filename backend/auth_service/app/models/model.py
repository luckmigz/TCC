from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
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
        orm_mode = True
