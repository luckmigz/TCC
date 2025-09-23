import json
import os
import re
import motor.motor_asyncio
import asyncio
from pydantic import BaseModel
from typing import Optional

# ===============================
# MODELS
# ===============================
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    password: str
    cpf: str  # CPF ou CNPJ

class Restaurant(BaseModel):
    id: Optional[str] = None
    name: str 
    email: str
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

# ===============================
# DATABASE
# ===============================
MONGODB_URL = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client["Usuarios"]

collection_users = db["users"]
collection_restaurants = db["restaurantes"]

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
def restaurant_helper(restaurant) -> dict:
    return {
        "id": str(restaurant["_id"]),
        "name": restaurant["name"],
        "email": restaurant["email"],
        "password": restaurant["password"],
        "address": restaurant["address"],
        "cep": restaurant["cep"],
        "cnpj": restaurant["cnpj"],
        "phone_number": restaurant["phone_number"],
        "cuisine_type": restaurant["cuisine_type"],
        "rating": restaurant["rating"],
        "is_open": restaurant["is_open"],
        "occupancy": restaurant["occupancy"],
        "max_occupancy": restaurant["max_occupancy"],
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

def get_user_type(document: str) -> str:
    if is_cpf(document):
        return "cpf"
    elif is_cnpj(document):
        return "cnpj"
    else:
        raise ValueError("Documento inválido. Deve ser CPF (11 dígitos) ou CNPJ (14 dígitos)")
# ===============================
# SERVICE
# ===============================
async def create_user(user: User) -> dict:
    collection = get_collection_by_document(user.cpf)
    user_type = get_user_type(user.cpf)

    existing_user = await collection.find_one({"cpf":user.cpf})
    if existing_user:
        doc_type = "CPF" if user_type == "cpf" else "CNPJ"
        raise ValueError(f"Usuário com este {doc_type} já existe")

    user_dict = user.dict(exclude={"id"})
    result = await collection.insert_one(user_dict)
    new_user = await collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)
async def get_user_email(email: str) -> User:
    user_cpf = await collection_users.find_one({"email": email})
    user_cnpj = await collection_restaurants.find_one({"email": email})
    user = user_cpf or user_cnpj
    if not user:
        raise ValueError("Usuário não encontrado")
    return User(**user_helper(user))

async def get_user_cpf(cpf: str) -> User:
    collection = get_collection_by_document(cpf)
    user = await collection.find_one({"cpf": cpf})
    if not user:
        raise ValueError("Usuário não encontrado")
    return User(**user_helper(user))

async def update_user(user: User) -> dict:
    collection = get_collection_by_document(user.cpf)
    existing_user = await collection.find_one({"cpf": user.cpf})
    if not existing_user:
        raise ValueError("Usuário não encontrado")
    user_dict = user.dict(exclude={"id"})
    await collection.update_one({"cpf": user.cpf}, {"$set": user_dict})
    updated_user = await collection.find_one({"cpf": user.cpf})
    return user_helper(updated_user)

async def delete_user(email: str) -> dict:
    user_cpf = await collection_users.find_one({"email": email})
    user_cnpj = await collection_restaurants.find_one({"email": email})
    user = user_cpf or user_cnpj
    if not user:
        raise ValueError("Usuário não encontrado")
    collection = collection_users if user_cpf else collection_restaurants
    result = await collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise ValueError("Erro ao deletar usuário")
    return {"success": True, "message": "Usuário deletado com sucesso"}
# ===============================
# SERVICE - RESTAURANTS
# ===============================
async def create_restaurant(restaurant: Restaurant) -> dict:
    existing = await collection_restaurants.find_one({"cnpj": restaurant.cnpj})
    if existing:
        raise ValueError("Restaurante com este CNPJ já existe")
    rest_dict = restaurant.dict(exclude={"id"})
    result = await collection_restaurants.insert_one(rest_dict)
    new_restaurant = await collection_restaurants.find_one({"_id": result.inserted_id})
    return restaurant_helper(new_restaurant)

async def update_restaurant(restaurant: Restaurant) -> dict:
    existing = await collection_restaurants.find_one({"cnpj": restaurant.cnpj})
    if not existing:
        raise ValueError("Restaurante não encontrado")
    rest_dict = restaurant.dict(exclude={"id"})
    await collection_restaurants.update_one({"cnpj": restaurant.cnpj}, {"$set": rest_dict})
    updated = await collection_restaurants.find_one({"cnpj": restaurant.cnpj})
    return restaurant_helper(updated)

async def delete_restaurant(cnpj: str) -> dict:
    result = await collection_restaurants.delete_one({"cnpj": cnpj})
    if result.deleted_count == 0:
        raise ValueError("Restaurante não encontrado")
    return {"success": True, "message": "Restaurante deletado com sucesso"}

async def get_restaurant_cnpj(cnpj: str) -> dict:
    restaurant = await collection_restaurants.find_one({"cnpj": cnpj})
    if not restaurant:
        raise ValueError("Restaurante não encontrado")
    return restaurant_helper(restaurant)
async def update_restaurant_occupancy(cnpj: str, new_occupancy: int) -> dict:
    # Verifica se o restaurante existe
    existing = await collection_restaurants.find_one({"cnpj": cnpj})
    if not existing:
        raise ValueError("Restaurante não encontrado")

    # Atualiza apenas o campo de ocupação
    result = await collection_restaurants.update_one(
        {"cnpj": cnpj},
        {"$set": {"occupancy": new_occupancy}}
    )

    if result.matched_count == 0:
        raise ValueError("Erro ao atualizar ocupação")

    # Retorna restaurante atualizado
    updated = await collection_restaurants.find_one({"cnpj": cnpj})
    return restaurant_helper(updated)
# ===============================
# LAMBDA HANDLER
# ===============================
def lambda_handler(event, context):
    try:
        method = event.get("httpMethod", "POST")
        body = json.loads(event.get("body", "{}"))

        loop = asyncio.get_event_loop()

        if method == "POST":
            if body.get("cnpj"):
                obj = Restaurant(**body)
                result = loop.run_until_complete(create_restaurant(obj))
            elif body.get("cpf"):
                cpf = body["cpf"]
                result = loop.run_until_complete(get_user_cpf(cpf))

        elif method == "GET":
            if body.get("cnpj"):
                cnpj = body["cnpj"]
                result = loop.run_until_complete(get_restaurant_cnpj(cnpj))
            elif body.get("email"):
                email = body["email"]
                result = loop.run_until_complete(get_user_email(email))
            elif body.get("cpf"):
                cpf = body["cpf"]
                result = loop.run_until_complete(get_user_cpf(cpf))

        elif method == "PUT":
            if body.get("cnpj") and "occupancy" in body:
                cnpj = body["cnpj"]
                new_occupancy = body["occupancy"]
                result = loop.run_until_complete(update_restaurant_occupancy(cnpj, new_occupancy))
            elif body.get("cpf"):
                obj = User(**body)
                result = loop.run_until_complete(create_user(obj))
            elif body.get("cnpj"):
                obj = Restaurant(**body)
                result = loop.run_until_complete(update_restaurant(obj))


        elif method == "DELETE":
            if body.get("cnpj"):
                cnpj = body["cnpj"]
                result = loop.run_until_complete(delete_restaurant(cnpj))

            elif  body.get("email"):
                email = body["email"]
                result = loop.run_until_complete(delete_user(email))

        else:
            raise ValueError("Operação não suportada ou dados ausentes")

        return {
            "statusCode": 200 if method != "POST" else 201,
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
