# routes/reports_routes.py

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

from ..service.reports_generator_db import gerar_relatorio_diario_total

# --- Configurações Mongo (mesmas do analytics_routes) ---
MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "Usuarios"
COLLECTION_REPORTS = "analytics_reports"  # nova coleção para relatórios


# --- Cria o router de relatórios ---
router = APIRouter(prefix="/reports", tags=["Reports"])


# =====================================================
# 🔹 Modelo do corpo da requisição
# =====================================================
class RelatorioRequest(BaseModel):
    cnpj: str


# =====================================================
# 🔹 Rota POST — gera e salva relatório diário/total
# =====================================================
@router.post("/generate", response_model=Dict[str, Any], status_code=201)
async def gerar_relatorio_route(payload: RelatorioRequest):
    """
    Gera e salva um relatório diário + total (YOLO + LLaMA) para o restaurante informado.
    O frontend deve enviar um JSON com o campo "cnpj".
    Exemplo:
    {
        "cnpj": "12345678000199"
    }
    """
    try:
        cnpj = payload.cnpj
        print(f"📊 Recebida requisição para gerar RELATÓRIO de {cnpj}...")

        # 1️⃣ Gera o relatório (sem mexer em banco)
        relatorio = await gerar_relatorio_diario_total(cnpj)
        print("✅ Relatório gerado com sucesso!")

        # 2️⃣ Conecta ao banco e salva o documento
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        colecao_relatorios = db[COLLECTION_REPORTS]

        doc = {
            "cnpj": cnpj,
            "cnpj_normalizado": relatorio["cnpj_normalizado"],
            "timestamp": datetime.utcnow(),
            "yolo_report": relatorio["yolo_report"],
            "llama_report": relatorio["llama_report"],
        }

        resultado = await colecao_relatorios.insert_one(doc)
        client.close()

        print(f"💾 Relatório salvo com _id: {resultado.inserted_id}")

        # 3️⃣ Retorna resposta para o frontend
        return {
            "message": "Relatório gerado e salvo com sucesso!",
            "cnpj": cnpj,
            "mongo_id": str(resultado.inserted_id),
            "yolo_report": relatorio["yolo_report"],
            "llama_report": relatorio["llama_report"],
        }

    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")
