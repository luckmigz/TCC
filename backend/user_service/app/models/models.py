from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[int] 
    name: str
    email: EmailStr
    password: str

