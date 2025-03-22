from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas.user.user_schema_request_create import UserSchemaRequestCreate
from api.schemas.user.user_schema_response import UserSchemaResponse
from api.schemas.user.user_schmea_request_update import UserSchemaRequestUpdate
from api.service.user_service import UserService, get_user_service

router = APIRouter(tags=["users"], prefix="/users")


@router.post("/", response_model=UserSchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserSchemaRequestCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Создание нового пользователя
    """
    # TODO: Реализовать создание пользователя
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/{user_id}", response_model=UserSchemaResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Получение пользователя по ID
    """
    # TODO: Реализовать получение пользователя
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.put("/{user_id}", response_model=UserSchemaResponse)
async def update_user(
    user_id: str,
    user: UserSchemaRequestUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Обновление данных пользователя
    """
    # TODO: Реализовать обновление пользователя
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Удаление пользователя
    """
    # TODO: Реализовать удаление пользователя
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/me", response_model=UserSchemaResponse)
async def get_current_user(
    user_service: UserService = Depends(get_user_service)
):
    """
    Получение информации о текущем авторизованном пользователе
    """
    # TODO: Реализовать получение текущего пользователя
    raise HTTPException(status_code=501, detail="Not Implemented")
