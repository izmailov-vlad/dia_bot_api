from fastapi import APIRouter, Depends, HTTPException, status
from api.auth.middleware.auth_middleware import get_current_user
from api.user.repository.user_repository import UserRepository, get_user_repository
from api.user.schemas.user_schema_response import UserSchemaResponse
from api.user.schemas.user_schmea_request_update import UserSchemaRequestUpdate
from api.user.service.user_service import UserService, get_user_service
from database.models.user.user_model import UserModel

router = APIRouter(tags=["users"], prefix="/users")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: UserModel = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Удаление пользователя
    """
    user_repository.delete_current(current_user.id)
    return {}


@router.get("/me", response_model=UserSchemaResponse)
async def get_current_user(
    current_user: UserModel = Depends(get_current_user),
):
    """
    Получение информации о текущем авторизованном пользователе
    """
    return current_user
