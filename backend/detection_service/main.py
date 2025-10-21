from fastapi import FastAPI
from routes import camera_routes
import uvicorn

# O app é definido ANTES do uvicorn.run
app = FastAPI(title="IA Camera Service", version="1.0")

# Inclui as rotas definidas em camera_routes.py
app.include_router(camera_routes.router, prefix="/camera", tags=["Camera"])

@app.get("/")
async def root():
    return {"message": "IA Camera Service ativo 🚀"}

# O uvicorn.run deve verificar o __name__ para permitir a importação do 'app'
if __name__ == "__main__":
    # Recarrega o serviço quando o código é alterado
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)