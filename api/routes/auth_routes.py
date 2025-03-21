from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from api.service.auth_service import AuthService
from api.schemas.token.token_schema import TokenSchema, RefreshTokenRequest
from api.middleware.auth_middleware import get_current_user
from database.models.user.user_model import User

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login", response_model=TokenSchema)
def login(
    telegram_id: str,
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя и получение токенов"""
    auth_service = AuthService(db)

    user = auth_service.authenticate_user(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_tokens(user.id)


@router.post("/refresh", response_model=TokenSchema)
def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Обновление пары токенов через refresh токен"""
    auth_service = AuthService(db)

    new_tokens = auth_service.refresh_tokens(token_data.refresh_token)
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return new_tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Выход из системы (отзыв всех refresh токенов)"""
    auth_service = AuthService(db)
    auth_service.revoke_tokens(user.id)
    return {}
