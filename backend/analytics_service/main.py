# main.py
from fastapi import FastAPI
import uvicorn
from routes import analytics_routes


app = FastAPI(title="IA Camera Service", version="1.0")

# Prefixo /camera (como você já fazia)
app.include_router(analytics_routes.router)

@app.get("/")
async def root():
    return {"message": "IA Camera Service ativo 🚀"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
