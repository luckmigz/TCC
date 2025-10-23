from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from ..service.data_processor_db import gerar_analises_duplas

# --- Configurações Mongo ---
MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "Usuarios"
COLLECTION_ANALYTICS = "analytics"

# --- Cria o router principal ---
router = APIRouter(prefix="/analytics", tags=["Analytics"])


# =====================================================
# 🔹 Modelo do corpo da requisição
# =====================================================
class AnaliseRequest(BaseModel):
    cnpj: str


# =====================================================
# 🔹 Rota POST — gera e salva análises
# =====================================================
@router.post("/generate", response_model=Dict[str, Any], status_code=201)
async def gerar_analise_route(payload: AnaliseRequest):
    """
    Gera e salva uma análise (YOLO + LLaMA) para o restaurante informado.
    O frontend deve enviar um JSON com o campo "cnpj".
    Exemplo:
    {
        "cnpj": "12345678000199"
    }
    """
    try:
        cnpj = payload.cnpj
        print(f"📊 Recebida requisição para gerar análise de {cnpj}...")

        # 1️⃣ Gera as análises (usa o módulo de processamento)
        analises = await gerar_analises_duplas(cnpj)
        print("✅ Análises geradas com sucesso!")

        # 2️⃣ Conecta ao banco e salva o documento
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        colecao_analises = db[COLLECTION_ANALYTICS]

        doc = {
            "cnpj": cnpj,
            "timestamp": datetime.utcnow(),
            "yolo_analysis": analises["yolo_analysis"],
            "llama_analysis": analises["llama_analysis"]
        }

        resultado = await colecao_analises.insert_one(doc)
        client.close()

        print(f"💾 Documento salvo com _id: {resultado.inserted_id}")

        # 3️⃣ Retorna resposta para o frontend
        return {
            "message": "Análise gerada e salva com sucesso!",
            "cnpj": cnpj,
            "mongo_id": str(resultado.inserted_id),
            "yolo_analysis": analises["yolo_analysis"],
            "llama_analysis": analises["llama_analysis"],
        }

    except Exception as e:
        print(f"❌ Erro ao gerar análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar análise: {str(e)}")
