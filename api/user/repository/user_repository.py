from fastapi import Depends

from api.task.service.task_service import TaskService
from api.user.service.user_service import UserService, get_user_service


class UserRepository:
    """
    Репозиторий для работы с пользователями.
    Выступает в роли промежуточного слоя между контроллерами и сервисом.
    Делегирует выполнение операций сервису UserService.
    """

    def __init__(self, user_service: UserService, task_service: TaskService):
        """
        Инициализирует репозиторий
        """

        self.user_service = user_service
        self.task_service = task_service

    def delete_current(self, user_id: str) -> bool:
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
