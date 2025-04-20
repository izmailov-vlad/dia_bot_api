from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from api.auth.service.auth_service import AuthService, get_auth_service
from api.auth.schemas.token_schema import TokenSchema
from api.auth.schemas.auth_register_schema import AuthRegisterSchema
from api.auth.schemas.auth_login_schema import AuthLoginSchema
from api.user.service.user_service import UserService, get_user_service
from database.database import get_db


class AuthRepository:
    """
    Репозиторий для работы с авторизацией.
    Выступает в роли промежуточного слоя между контроллерами и сервисом.
    Делегирует выполнение операций сервису AuthService.
    """

    def __init__(self, db: Session, auth_service: AuthService, user_service: UserService):
        """
        Инициализирует репозиторий
        """
        self.auth_service = auth_service
        self.user_service = user_service
        self.db_session = db

    def refresh_tokens(self, refresh_token: str) -> Optional[TokenSchema]:
        """
        Обновление пары токенов по refresh токену
        """
        return self.auth_service.refresh_tokens(refresh_token)

    def revoke_tokens(self, user_id: str) -> bool:
        """
        Отзыв всех refresh токенов пользователя
        """
        return self.auth_service.revoke_tokens(user_id)

    def register(self, user_data: AuthRegisterSchema) -> TokenSchema:
        """Регистрация нового пользователя"""
        return self.auth_service.register(user_data)

    def login(self, user_data: AuthLoginSchema) -> TokenSchema:
        """Авторизация пользователя"""
        return self.auth_service.login(user_data)

# Функция для внедрения зависимости


def get_auth_repository(
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> AuthRepository:
    """
    Возвращает экземпляр AuthRepository для внедрения зависимости.
    """
    return AuthRepository(db, auth_service, user_service)
