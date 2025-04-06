import logging
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import Depends
from sqlalchemy.future import select
from sqlalchemy import update, delete
from api.task.schemas.task.task_response_schema import TaskResponseSchema
from api.task.schemas.task.task_create_schema import TaskCreateSchema
from api.task.schemas.task.task_update_schema import TaskUpdateSchema
from database.database import get_db
from database.models.task.task_model import TaskModel
from sqlalchemy.orm import Session

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)


class TaskService:
    def __init__(
        self,
        db_session: Session,
    ):
        self.db_session = db_session

    async def create_task(
        self,
        task: TaskCreateSchema,
        user_id: str
    ) -> TaskResponseSchema:
        """Создать новую задачу"""
        try:
            task_id = str(uuid4())
            new_task = TaskModel(
                id=task_id,
                user_id=user_id,
                title=task.title,
                description=task.description,
                start_time=task.start_time,
                end_time=task.end_time,
                reminder=task.reminder,
                mark=task.mark,
                status=task.status,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.db_session.add(new_task)
            self.db_session.commit()
            self.db_session.refresh(new_task)
            # Создание ответа
            response = TaskResponseSchema(
                id=task_id,
                title=new_task.title,
                description=new_task.description,
                start_time=new_task.start_time,
                end_time=new_task.end_time,
                reminder=new_task.reminder,
                mark=new_task.mark,
                status=new_task.status,
            )

            return response

        except Exception as e:
            logger.error(
                f"Ошибка при создании задачи: {str(e)}", exc_info=True)
            logger.debug(f"Тип исключения: {type(e).__name__}")
            logger.debug(f"Аргументы исключения: {e.args}")
            logger.debug("=== ОШИБКА СОЗДАНИЯ ЗАДАЧИ ===")
            raise

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[TaskResponseSchema]:
        """Получить задачу по ID"""

        try:
            query = select(TaskModel).where(
                TaskModel.id == task_id,
                TaskModel.user_id == user_id,
            )
            result = self.db_session.execute(query)
            task = result.scalars().first()

            if task is None:
                return None

            response = TaskResponseSchema(
                id=task.id,
                title=task.title,
                description=task.description,
                start_time=task.start_time,
                end_time=task.end_time,
                reminder=task.reminder,
                mark=task.mark,
                status=task.status,
            )
            return response

        except Exception as e:
            logger.error(
                f"Ошибка при получении задачи: {str(e)}", exc_info=True)
            logger.debug(f"Тип исключения: {type(e).__name__}")
            logger.debug(f"Аргументы исключения: {e.args}")
            logger.debug("=== ОШИБКА ПОЛУЧЕНИЯ ЗАДАЧИ ПО ID ===")
            raise

    async def get_all_tasks(self, user_id: str) -> List[TaskResponseSchema]:
        """
        Получить все задачи пользователя

        Args:
            user_id: ID пользователя

        Returns:
            List[TaskSchemaResponse]: Список задач, принадлежащих указанному пользователю
        """
        try:
            query = select(TaskModel).where(TaskModel.user_id == user_id)
            result = self.db_session.execute(query)
            tasks = result.scalars().all()
            task_responses = [
                TaskResponseSchema(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    start_time=task.start_time,
                    end_time=task.end_time,
                    reminder=task.reminder,
                    mark=task.mark,
                    status=task.status,
                ) for task in tasks
            ]

            return task_responses

        except Exception as e:
            logger.error(
                f"Ошибка при получении задач пользователя: {str(e)}", exc_info=True)
            raise

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        new_task: TaskUpdateSchema,
    ) -> Optional[TaskResponseSchema]:
        """Обновить задачу"""

        task = await self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        update_data = {}
        # Добавляем новые поля в обновление
        for field in ['title', 'description', 'start_time', 'end_time',
                      'reminder', 'mark', 'status']:
            if hasattr(new_task, field) and getattr(new_task, field) is not None:
                update_data[field] = getattr(new_task, field)

        update_data["updated_at"] = datetime.now()

        query = update(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.user_id == user_id
        ).values(**update_data)

        self.db_session.execute(query)
        self.db_session.commit()

        return await self.get_task_by_id(task_id, user_id)

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Удалить задачу"""

        task = await self.get_task_by_id(task_id, user_id)
        if not task:
            return False

        query = delete(TaskModel).where(
            TaskModel.id == task_id, TaskModel.user_id == user_id)
        self.db_session.execute(query)
        self.db_session.commit()

        return True

    async def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TaskResponseSchema]:
        """Получить задачи в заданном временном диапазоне"""

        query = select(TaskModel).where(
            TaskModel.start_time >= start_date,
            TaskModel.end_time <= end_date
        )
        result = self.db_session.execute(query)
        tasks = result.scalars().all()

        return [
            TaskResponseSchema(
                id=task.id,
                title=task.title,
                description=task.description,
                start_time=task.start_time,
                end_time=task.end_time
            ) for task in tasks
        ]


def get_task_service(
    db: Session = Depends(get_db),
) -> TaskService:
    """
    Зависимость для получения Task сервиса
    """
    return TaskService(db)
