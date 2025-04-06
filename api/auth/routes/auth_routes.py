from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.repository.auth_repository import AuthRepository, get_auth_repository
from api.schemas.user.user_schema_request_create import UserSchemaRequestCreate
from api.auth.schemas.token_schema import TokenSchema, RefreshTokenRequest
from api.middleware.auth_middleware import get_current_user
from database.models.user.user_model import UserModel

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login", response_model=TokenSchema)
def login(
    telegram_id: str,
    auth_repository: AuthRepository = Depends(get_auth_repository)
):
    """Аутентификация пользователя и получение токенов"""
    user = auth_repository.authenticate_user(telegram_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_repository.create_tokens(user.id)


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


@router.post("/register", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserSchemaRequestCreate,
    auth_repository: AuthRepository = Depends(get_auth_repository)
):
    """
    Регистрация нового пользователя

    - Проверяет, существует ли пользователь с таким telegram_id
    - Если нет, создает нового пользователя
    - Возвращает access и refresh токены
    """
    return auth_repository.register_user(user_data)
