import re
from ..models.models import User
import motor.motor_asyncio
import os 

TIMEOUT = 5  # segundos

MONGODB_URL = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client["Usuarios"]

collection_users = db["users"]
collection_restaurants = db["restaurantes"]

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)


# Duas coleções diferentes: users (CPF) e restaurants (CNPJ)
collection_users = db["users"]        # Para usuários pessoa física (CPF)
collection_restaurants = db["restaurants"]  # Para usuários pessoa jurídica (CNPJ)

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
        "cpf": user["cpf"],
    }

def is_cpf(document: str) -> bool:
    """Verifica se o documento é um CPF (11 dígitos)"""
    # Remove caracteres não numéricos
    clean_doc = re.sub(r'\D', '', document)
    return len(clean_doc) == 11

def is_cnpj(document: str) -> bool:
    """Verifica se o documento é um CNPJ (14 dígitos)"""
    # Remove caracteres não numéricos
    clean_doc = re.sub(r'\D', '', document)
    return len(clean_doc) == 14

def get_collection_by_document(document: str):
    """Retorna a coleção apropriada baseada no tipo de documento"""
    if is_cpf(document):
        return collection_users
    elif is_cnpj(document):
        return collection_restaurants
    else:
        raise ValueError("Documento inválido. Deve ser CPF (11 dígitos) ou CNPJ (14 dígitos)")

def get_user_type(document: str) -> str:
    """Retorna o tipo do usuário baseado no documento"""
    if is_cpf(document):
        return "cpf"
    elif is_cnpj(document):
        return "cnpj"
    else:
        raise ValueError("Documento inválido. Deve ser CPF (11 dígitos) ou CNPJ (14 dígitos)")
    


async def create_user(user: User) -> User:
    # Determinar qual coleção usar baseada no tipo de documento
    collection = get_collection_by_document(user.cpf)
    user_type = get_user_type(user.cpf)
    
    # Verificar se já existe um usuário com este documento
    existing_user = await collection.find_one({"cpf": user.cpf})
    if existing_user:
        doc_type = "CPF" if user_type == "cpf" else "CNPJ"
        raise ValueError(f"Usuário com este {doc_type} já existe")
    
    user_dict = user.model_dump(exclude={"id"})
    result = await collection.insert_one(user_dict)
    new_user = await collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)
    
async def get_user_email(email: str) -> User:
    # Buscar em ambas as coleções
    user_cpf = await collection_users.find_one({"email": email})
    user_cnpj = await collection_restaurants.find_one({"email": email})
    
    user = user_cpf or user_cnpj
    if not user:
        raise ValueError("Usuário não encontrado")
    
    return User(**user_helper(user))

async def get_user_cpf(cpf: str) -> User:
    # Determinar qual coleção usar baseada no tipo de documento
    try:
        collection = get_collection_by_document(cpf)
        user = await collection.find_one({"cpf": cpf})
        
        if not user:
            raise ValueError("Usuário não encontrado")
        
        return User(**user_helper(user))
    except ValueError as e:
        # Se o documento for inválido, propagar o erro
        raise e


async def update_user(user: User) -> User:
    # Determinar qual coleção usar baseada no tipo de documento
    collection = get_collection_by_document(user.cpf)
    
    # Verificar se o usuário existe
    existing_user = await collection.find_one({"cpf": user.cpf})
    if not existing_user:
        raise ValueError("Usuário não encontrado")
    
    # Atualizar o usuário
    user_dict = user.model_dump(exclude={"id"})
    result = await collection.update_one(
        {"cpf": user.cpf}, 
        {"$set": user_dict}
    )
    
    if result.matched_count == 0:
        raise ValueError("Erro ao atualizar usuário")
    
    # Buscar o usuário atualizado
    updated_user = await collection.find_one({"cpf": user.cpf})
    return user_helper(updated_user)

async def delete_user(email: str) -> dict:
    # Buscar o usuário em ambas as coleções para encontrar onde está
    user_cpf = await collection_users.find_one({"email": email})
    user_cnpj = await collection_restaurants.find_one({"email": email})
    
    user = user_cpf or user_cnpj
    if not user:
        raise ValueError("Usuário não encontrado")
    
    # Determinar qual coleção usar
    collection = collection_users if user_cpf else collection_restaurants
    
    # Deletar o usuário
    result = await collection.delete_one({"email": email})
    
    if result.deleted_count == 0:
        raise ValueError("Erro ao deletar usuário")
    
    return {"success": True, "message": "Usuário deletado com sucesso"}
