from fastapi import FastAPI
from .routes import detection

app = FastAPI(
    title="Detection Service API",
    description="API para obter dados de detecção de objetos.",
    version="1.0.0"
)

app.include_router(detection.router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API do Serviço de Detecção."}