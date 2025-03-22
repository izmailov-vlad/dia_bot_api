from typing import List, Optional
from datetime import datetime
from fastapi import Depends
from openai import OpenAI

from api.service.task.task_service import TaskService
from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.schemas.task.task_schema_response_gpt import TaskSchemaResponseGpt
from database.database import get_db
from sqlalchemy.orm import Session

from dependencies import get_open_ai_client


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

    async def generate_task_gpt(self, request: str) -> TaskSchemaResponseGpt:
        """
        Генерирует задачу с помощью GPT на основе текстового запроса

        Args:
            request: Текстовый запрос для создания задачи

        Returns:
            TaskSchemaResponseGpt: Сгенерированная задача
        """
        return await self.task_service.generate_task_gpt(request)

    async def create_task_gpt(self, request: str, user_id: str) -> TaskSchemaResponse:
        """
        Создаёт задачу с помощью GPT
        """
        gpt_task = await self.task_service.generate_task_gpt(request)
        task_data = TaskSchemaCreate(
            title=gpt_task.title,
            start_time=gpt_task.start_time,
            end_time=gpt_task.end_time
        )
        return await self.task_service.create_task(task=task_data, user_id=user_id)

    async def create_task(self, task: TaskSchemaCreate, user_id: str) -> TaskSchemaResponse:
        """
        Создаёт новую задачу

        Args:
            task: Данные для создания задачи
            user_id: ID пользователя, создающего задачу

        Returns:
            TaskSchemaResponse: Созданная задача
        """
        return await self.task_service.create_task(task, user_id)

    async def get_task_by_id(self, task_id: str) -> Optional[TaskSchemaResponse]:
        """
        Получает задачу по ID

        Args:
            task_id: ID задачи

        Returns:
            Optional[TaskSchemaResponse]: Найденная задача или None
        """
        return await self.task_service.get_task_by_id(task_id)

    async def get_all_tasks(self) -> List[TaskSchemaResponse]:
        """
        Получает все задачи

        Returns:
            List[TaskSchemaResponse]: Список всех задач
        """
        return await self.task_service.get_all_tasks()

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Optional[TaskSchemaResponse]:
        """
        Обновляет задачу

        Args:
            task_id: ID задачи
            title: Новый заголовок (опционально)
            description: Новое описание (опционально)
            start_time: Новое время начала (опционально)
            end_time: Новое время окончания (опционально)

        Returns:
            Optional[TaskSchemaResponse]: Обновленная задача или None
        """
        return await self.task_service.update_task(
            task_id, title, description, start_time, end_time
        )

    async def delete_task(self, task_id: str) -> bool:
        """
        Удаляет задачу

        Args:
            task_id: ID задачи

        Returns:
            bool: True, если задача успешно удалена, иначе False
        """
        return await self.task_service.delete_task(task_id)

    async def get_tasks_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[TaskSchemaResponse]:
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
    db: Session = Depends(get_db),
    client: OpenAI = Depends(get_open_ai_client)
) -> TaskRepository:
    """
    Возвращает экземпляр TaskRepository для внедрения зависимости.

    Args:
        db: Сессия базы данных
        client: Клиент OpenAI

    Returns:
        TaskRepository: Репозиторий для работы с задачами
    """
    task_service = TaskService(db, client)
    return TaskRepository(task_service)
