# main.py
from fastapi import FastAPI
from routes import camera_routes
import uvicorn

app = FastAPI(title="IA Camera Service", version="1.0")

# Prefixo /camera (como você já fazia)
app.include_router(camera_routes.router, prefix="/camera", tags=["Camera"])

@app.get("/")
async def root():
    return {"message": "IA Camera Service ativo 🚀"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
