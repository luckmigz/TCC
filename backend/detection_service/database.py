import os
from pymongo import MongoClient
import logging

MONGO_URI = os.environ.get("MONGODB_URI")
DB_NAME = "tcc_ia_service"

if not MONGO_URI:
    logging.critical("A variável de ambiente MONGODB_URI não foi definida!")
    exit()

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    detections_collection = db["detections"]
    control_collection = db["control_signals"]
    logging.info("✅ Conexão com o MongoDB estabelecida.")
except Exception as e:
    logging.critical(f"🔥 Falha ao conectar com o MongoDB: {e}")
    exit()