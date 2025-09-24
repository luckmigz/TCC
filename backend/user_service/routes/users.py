from fastapi import APIRouter, HTTPException
from user_service.app.models.models import User
from user_service.app.service.service import create_user, get_user_email, get_user_cpf, update_user, delete_user

router = APIRouter()

@router.post("/create", response_model=dict, status_code=201)
async def create_user_route(user: User):
    try:
        result = await create_user(user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

