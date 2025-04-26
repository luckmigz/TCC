from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def restaurant_root():
    return {"message": "Restaurant Service Root"}
