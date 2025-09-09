import json
import os
import re
import motor.motor_asyncio
import asyncio
from pydantic import BaseModel, EmailStr
from typing import Optional

# ===============================
# MODELS
# ===============================
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    password: str
    cpf: str  # CPF ou CNPJ

# ===============================
# DATABASE
# ===============================
MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME", "userdb")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

collection_users = db["users"]
collection_restaurants = db["restaurants"]

# ===============================
# HELPERS
# ===============================
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
        "cpf": user["cpf"],
    }

def is_cpf(document: str) -> bool:
    clean_doc = re.sub(r'\D', '', document)
    return len(clean_doc) == 11

def is_cnpj(document: str) -> bool:
    clean_doc = re.sub(r'\D', '', document)
    return len(clean_doc) == 14

def get_collection_by_document(document: str):
    if is_cpf(document):
        return collection_users
    elif is_cnpj(document):
        return collection_restaurants
    else:
        raise ValueError("Documento inválido. Deve ser CPF (11 dígitos) ou CNPJ (14 dígitos)")

# ===============================
# SERVICE
# ===============================
async def create_user(user: User) -> dict:
    collection = get_collection_by_document(user.cpf)
    
    existing_user = await collection.find_one({"cpf": user.cpf})
    if existing_user:
        raise ValueError("Usuário com este CPF/CNPJ já existe")
    
    user_dict = user.dict(exclude={"id"})
    result = await collection.insert_one(user_dict)
    new_user = await collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

# ===============================
# LAMBDA HANDLER
# ===============================
def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        user = User(**body)
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(create_user(user))
        
        return {
            "statusCode": 201,
            "body": json.dumps(result)
        }
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
