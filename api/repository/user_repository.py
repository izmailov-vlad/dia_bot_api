from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from api.service.task.task_service import TaskService
from api.service.user_service import UserService, get_user_service
from api.schemas.user.user_schema_request_create import UserSchemaRequestCreate
from api.schemas.user.user_schema_response import UserSchemaResponse
from api.schemas.user.user_schmea_request_update import UserSchemaRequestUpdate


class UserRepository:
    """
    Репозиторий для работы с пользователями.
    Выступает в роли промежуточного слоя между контроллерами и сервисом.
    Делегирует выполнение операций сервису UserService.
    """

    def __init__(self, user_service: UserService, task_service: TaskService):
        """
        Инициализирует репозиторий

        Args:
            user_service: Сервис для работы с пользователями
            task_service: Сервис для работы с задачами
        """
        self.user_service = user_service
        self.task_service = task_service

    def create_user(self, user_data: UserSchemaRequestCreate) -> UserSchemaResponse:
        """
        Создаёт нового пользователя

        Args:
            user_data: Данные для создания пользователя

        Returns:
            UserSchemaResponse: Созданный пользователь

        Raises:
            HTTPException: Если пользователь с таким telegram_id уже существует
        """
        return self.user_service.create_user(user_data)

    def update_user(self, user_id: str, user_data: UserSchemaRequestUpdate) -> Optional[UserSchemaResponse]:
        """
        Обновляет данные пользователя

        Args:
            user_id: ID пользователя
            user_data: Данные для обновления

        Returns:
            Optional[UserSchemaResponse]: Обновленный пользователь или None, если пользователь не найден

        Raises:
            HTTPException: Если при обновлении возникают конфликты (например, telegram_id уже занят)
        """
        return self.user_service.update_user(user_id, user_data)

    def delete_user(self, user_id: str) -> bool:
        """
        Удаляет пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь был удален, False если пользователь не найден
        """
        return self.user_service.delete_user(user_id)

    def get_user_smart_tags(self, user_id: str):
        """
        Получает умные теги пользователя

        Args:
            user_id: ID пользователя

        Returns:
            List[SmartTagSchemaResponse]: Список умных тегов пользователя

        Raises:
            HTTPException: Если пользователь не найден
        """
        return self.user_service.get_user_smart_tags(user_id)


# Функция для внедрения зависимости
def get_user_repository(user_service: UserService = Depends(get_user_service)) -> UserRepository:
    """
    Возвращает экземпляр UserRepository для внедрения зависимости.

    Args:
        user_service: Сервис для работы с пользователями

    Returns:
        UserRepository: Репозиторий для работы с пользователями
    """
    return UserRepository(user_service)
