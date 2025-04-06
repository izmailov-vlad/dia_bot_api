from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from api.auth.service.auth_service import AuthService
from api.auth.schemas.token_schema import TokenSchema
from api.schemas.user.user_schema_request_create import UserSchemaRequestCreate
from api.user.service.user_service import UserService
from database.models.user.user_model import UserModel
from database.database import get_db


class AuthRepository:
    """
    Репозиторий для работы с авторизацией.
    Выступает в роли промежуточного слоя между контроллерами и сервисом.
    Делегирует выполнение операций сервису AuthService.
    """

    def __init__(self, auth_service: AuthService, user_service: UserService):
        """
        Инициализирует репозиторий

        Args:
            auth_service: Сервис для работы с авторизацией
            user_service: Сервис для работы с пользователями
        """
        self.auth_service = auth_service
        self.user_service = user_service
        self.db_session = auth_service.db_session

    def authenticate_user(self, telegram_id: str) -> Optional[UserModel]:
        """
        Аутентификация пользователя по telegram_id

        Args:
            telegram_id: Идентификатор пользователя в Telegram

        Returns:
            Optional[UserModel]: Найденный пользователь или None
        """
        return self.auth_service.authenticate_user(telegram_id)

    def create_tokens(self, user_id: str) -> TokenSchema:
        """
        Создание пары токенов (access и refresh)

        Args:
            user_id: ID пользователя

        Returns:
            TokenSchema: Созданные токены
        """
        return self.auth_service.create_tokens(user_id)

    def validate_access_token(self, token: str) -> Optional[str]:
        """
        Проверка access токена

        Args:
            token: JWT access токен

        Returns:
            Optional[str]: ID пользователя, если токен валидный, иначе None
        """
        return self.auth_service.validate_access_token(token)

    def refresh_tokens(self, refresh_token: str) -> Optional[TokenSchema]:
        """
        Обновление пары токенов по refresh токену

        Args:
            refresh_token: Refresh токен

        Returns:
            Optional[TokenSchema]: Новые токены, если refresh токен валидный, иначе None
        """
        return self.auth_service.refresh_tokens(refresh_token)

    def revoke_tokens(self, user_id: str) -> bool:
        """
        Отзыв всех refresh токенов пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True, если операция выполнена успешно
        """
        return self.auth_service.revoke_tokens(user_id)

    def register_user(self, user_data: UserSchemaRequestCreate) -> TokenSchema:
        """
        Регистрация нового пользователя

        Args:
            user_data: Данные для регистрации пользователя

        Returns:
            TokenSchema: Токены для нового пользователя

        Raises:
            HTTPException: Если пользователь с таким telegram_id уже существует
        """
        user = self.user_service.create_user(user_data)
        # Создаем и возвращаем токены
        return self.create_tokens(user.id)


# Функция для внедрения зависимости
def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    """
    Возвращает экземпляр AuthRepository для внедрения зависимости.

    Args:
        db: Сессия базы данных

    Returns:
        AuthRepository: Репозиторий для работы с авторизацией
    """
    auth_service = AuthService(db)
    user_service = UserService(db)
    return AuthRepository(auth_service, user_service)
