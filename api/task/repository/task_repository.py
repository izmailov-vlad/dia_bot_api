from typing import List, Optional
from datetime import datetime
from fastapi import Depends
from api.task.schemas.task.task_response_schema import TaskResponseSchema
from api.task.schemas.task.task_create_schema import TaskCreateSchema
from api.task.schemas.task.task_response_gpt_schema import TaskResponseGptSchema
from api.task.schemas.task.task_update_schema import TaskUpdateSchema
from api.task.service.task_service import TaskService, get_task_service


class TaskRepository:
    """
    Репозиторий для работы с задачами.
    Выступает в роли промежуточного слоя между контроллерами и сервисом.
    Делегирует выполнение операций сервису TaskService.
    """

    def __init__(self, task_service: TaskService):
        """
        Инициализирует репозиторий

        Args:
            task_service: Сервис для работы с задачами
        """
        self.task_service = task_service

    async def search_by_query(self, query: str, user_id: str) -> List[TaskResponseSchema]:
        """Поиск задач по запросу"""
        return await self.task_service.search_by_query(query, user_id)

    async def generate_task_gpt(self, request: str) -> TaskResponseGptSchema:
        """
        Генерирует задачу с помощью GPT на основе текстового запроса

        Args:
            request: Текстовый запрос для создания задачи

        Returns:
            TaskSchemaResponseGpt: Сгенерированная задача
        """
        return await self.task_service.generate_task_gpt(request)

    async def create_task_gpt(self, request: str, user_id: str) -> TaskResponseSchema:
        """
        Создаёт задачу с помощью GPT
        """
        gpt_task = await self.task_service.generate_task_gpt(request)
        task_data = TaskCreateSchema(
            title=gpt_task.title,
            start_time=gpt_task.start_time,
            end_time=gpt_task.end_time
        )
        return await self.task_service.create_task(task=task_data, user_id=user_id)

    async def create_task(self, task: TaskCreateSchema, user_id: str) -> TaskResponseSchema:
        """
        Создаёт новую задачу

        Args:
            task: Данные для создания задачи
            user_id: ID пользователя, создающего задачу

        Returns:
            TaskSchemaResponse: Созданная задача
        """
        return await self.task_service.create_task(task, user_id)

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[TaskResponseSchema]:
        """
        Получает задачу по ID

        Args:
            task_id: ID задачи

        Returns:
            Optional[TaskSchemaResponse]: Найденная задача или None
        """
        return await self.task_service.get_task_by_id(task_id, user_id)

    async def get_all_tasks(self, user_id: str) -> List[TaskResponseSchema]:
        """
        Получает все задачи

        Returns:
            List[TaskSchemaResponse]: Список всех задач
        """
        return await self.task_service.get_all_tasks(user_id)

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        task: TaskUpdateSchema,
    ) -> Optional[TaskResponseSchema]:
        """
        Обновляет задачу

        Args:
            task_id: ID задачи
            user_id: ID пользователя
            task: Данные для обновления задачи

        Returns:
            Optional[TaskSchemaResponse]: Обновленная задача или None
        """
        return await self.task_service.update_task(
            task_id, user_id, task
        )

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Удаляет задачу

        Args:
            task_id: ID задачи

        Returns:
            bool: True, если задача успешно удалена, иначе False
        """
        return await self.task_service.delete_task(task_id, user_id)

    async def get_tasks_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[TaskResponseSchema]:
        """
        Получает задачи в заданном временном диапазоне

        Args:
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            List[TaskSchemaResponse]: Список задач в указанном диапазоне
        """
        return await self.task_service.get_tasks_by_date_range(start_date, end_date)


def get_task_repository(
    task_service: TaskService = Depends(get_task_service)
) -> TaskRepository:
    """
    Возвращает экземпляр TaskRepository для внедрения зависимости.

    Args:
        db: Сессия базы данных
        client: Клиент OpenAI

    Returns:
        TaskRepository: Репозиторий для работы с задачами
    """
    return TaskRepository(task_service)
