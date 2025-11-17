# main.py
import os
from fastapi import FastAPI
import uvicorn

from .routes import analytics_routes
from .routes import reports_routes  # 🔹 novo import

app = FastAPI(title="IA Camera Service", version="1.0")

app.include_router(analytics_routes.router)
app.include_router(reports_routes.router)  # 🔹 adiciona as rotas de relatório


@app.get("/")
async def root():
    return {"message": "IA Camera Service ativo 🚀"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
