import motor.motor_asyncio
from datetime import datetime

# --- Configurações ---
MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "Usuarios"
COLLECTION_NAME = "raw_detections"

# --- Inicialização do cliente ---
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
raw_collection = db[COLLECTION_NAME]


async def enviar_dados_crus(cnpj: str, rtsp_url: str, detections_yolo: list, detections_llama: dict):
    """
    Envia os dados crus de detecção (YOLO + LLaMA) para o MongoDB.
    - YOLO: lista de objetos detectados com bounding boxes.
    - LLaMA: contagens semânticas retornadas pelo Groq.
    """
    doc = {
        "cnpj": cnpj,
        "rtsp_url": rtsp_url,
        "timestamp": datetime.utcnow(),
        "detections_yolo": detections_yolo,
        "detections_llama": detections_llama,
        "yolo_count": len(detections_yolo),
        "llama_count": len(detections_llama)
    }

    try:
        await raw_collection.insert_one(doc)
        print(f"📦 Dados inseridos para {cnpj}: {len(detections_yolo)} YOLO | LLaMA={detections_llama}")
    except Exception as e:
        print(f"❌ Erro ao inserir dados no MongoDB: {e}")
