from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def user_root():
    return {"message": "User Service Root"}
