from typing import List, Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from api.task.schemas.task.task_response_schema import TaskResponseSchema
from api.task.schemas.task.task_create_schema import TaskCreateSchema
from api.task.schemas.task.task_response_gpt_schema import TaskResponseGptSchema
from api.task.schemas.task.task_update_schema import TaskUpdateSchema
from api.task.service.task_service import TaskService, get_task_service
import logging

from database.models.task.task_model import TaskStatusModel

logger = logging.getLogger(__name__)


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

    async def mark_task_completed(self, task_id: str, user_id: str) -> Optional[TaskResponseSchema]:
        """
        Отмечает задачу как выполненную
        """
        try:
            task = await self.task_service.mark_task_completed(task_id, user_id)
            if not task:
                logger.warning(
                    f"Задача не найдена: task_id={task_id}, user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Задача не найдена"
                )
            return task
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Ошибка при отметке задачи как выполненной: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Произошла ошибка при отметке задачи как выполненной"
            )

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

    async def get_tasks_by_date(self, date: datetime, status: TaskStatusModel, user_id: str) -> List[TaskResponseSchema]:
        """
        Получает задачи на конкретный день

        Args:
            date: Дата, на которую нужно получить задачи
            user_id: ID пользователя

        Returns:
            List[TaskSchemaResponse]: Список задач на указанную дату
        """
        logger.info(
            f"Repository: Запрос задач для пользователя {user_id} на дату {date.date()}")
        try:
            tasks = await self.task_service.get_tasks_by_date(date, status, user_id)
            logger.info(f"Repository: Получено {len(tasks)} задач")
            return tasks
        except Exception as e:
            logger.error(
                f"Repository: Ошибка при получении задач: {str(e)}", exc_info=True)
            raise


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
