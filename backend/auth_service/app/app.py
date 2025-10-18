from fastapi import FastAPI
from .routes.auth import router as auth_router
import uvicorn
import os

app = FastAPI(
    title="Auth Service API",
    version="1.0.0",
    description="Serviço para autenticação de usuários"
)

app.include_router(auth_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)