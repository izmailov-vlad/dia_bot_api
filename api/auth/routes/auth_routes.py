from fastapi import APIRouter, Depends, HTTPException, status
from typing import Tuple

from api.auth.repository.auth_repository import AuthRepository, get_auth_repository
from api.auth.schemas.token_schema import TokenSchema, RefreshTokenRequest
from api.auth.schemas.auth_register_schema import AuthRegisterSchema
from api.auth.schemas.auth_login_schema import AuthLoginSchema
from api.auth.middleware.auth_middleware import get_current_user
from database.models.user.user_model import UserModel

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login", response_model=TokenSchema)
def login(
    user_data: AuthLoginSchema,
    auth_repository: AuthRepository = Depends(get_auth_repository)
):
    """Авторизация пользователя"""
    return auth_repository.login(user_data)


@router.post("/refresh", response_model=TokenSchema)
def refresh_token(
    token_data: RefreshTokenRequest,
    auth_repository: AuthRepository = Depends(get_auth_repository)
):
    """Обновление пары токенов через refresh токен"""
    new_tokens = auth_repository.refresh_tokens(token_data.refresh_token)

    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return new_tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    user: UserModel = Depends(get_current_user),
    auth_repository: AuthRepository = Depends(get_auth_repository)
):
    """Выход из системы (отзыв всех refresh токенов)"""
    auth_repository.revoke_tokens(user.id)
    return {}


@router.post("/register", response_model=TokenSchema)
def register(
    user_data: AuthRegisterSchema,
    auth_repository: AuthRepository = Depends(get_auth_repository)
):
    """Регистрация нового пользователя"""
    return auth_repository.register(user_data)
