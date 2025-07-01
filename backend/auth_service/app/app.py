from fastapi import FastAPI
from routes.auth import router as user_router
import uvicorn

app = FastAPI(
    title="User Service API",
    version="1.0.0",
    description="Serviço para gerenciamento de usuários"
)

app.include_router(user_router, prefix="/login", tags=["Users"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8003, reload=True)
