import motor.motor_asyncio
from datetime import datetime
import os


MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "Usuarios"
COLLECTION_NAME = "raw_detections" # Coleção para dados crus

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
raw_collection = db[COLLECTION_NAME]

async def enviar_dados_crus(cnpj: str, rtsp_url: str, detections_json: list):
    """
    Salva os dados crus da detecção no MongoDB com timestamp.
    """
    doc = {
        "cnpj": cnpj,
        "rtsp_url": rtsp_url,
        "timestamp": datetime.utcnow(), # Data/Hora universal (UTC)
        "detections": detections_json,
        "count": len(detections_json) # Adiciona contagem para facilitar queries
    }
    
    try:
        await raw_collection.insert_one(doc)
        print(f"📦 Dados inseridos para {cnpj} ({len(detections_json)} detecções).")
    except Exception as e:
        print(f"❌ Erro ao inserir dados no MongoDB: {e}")