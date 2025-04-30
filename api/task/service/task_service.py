import logging
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import update, delete
from api.task.schemas.task.task_response_schema import TaskResponseSchema
from api.task.schemas.task.task_create_schema import TaskCreateSchema
from api.task.schemas.task.task_update_schema import TaskUpdateSchema
from database.database import get_db
from database.models.task.task_model import TaskModel, TaskStatusModel
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
                date=task.date,
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
                date=new_task.date,
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
                date=task.date,
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

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        update_task_params: TaskUpdateSchema,
    ) -> Optional[TaskResponseSchema]:
        """
        Обновляет задачу в базе данных

        Args:
            task_id: ID задачи для обновления
            user_id: ID пользователя
            new_task: Данные для обновления задачи

        Returns:
            Optional[TaskResponseSchema]: Обновленная задача или None, если задача не найдена
        """
        # Проверяем существование задачи
        existing_task = await self.get_task_by_id(task_id, user_id)
        if not existing_task:
            logger.warning(
                f"Задача не найдена: task_id={task_id}, user_id={user_id}")
            return None

        # Подготавливаем данные для обновления
        update_task_params_dict = update_task_params.model_dump(
            exclude_unset=True
        )
        if not update_task_params_dict:
            logger.warning(f"Нет данных для обновления: task_id={task_id}")
            return existing_task

        # Добавляем время обновления
        update_task_params_dict["updated_at"] = datetime.now()

        # Выполняем обновление одним запросом
        query = update(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.user_id == user_id
        ).values(**update_task_params_dict)

        self.db_session.execute(query)
        self.db_session.commit()

        # Получаем обновленную задачу
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

    async def get_tasks_by_date(self, date: datetime, status: TaskStatusModel, user_id: str) -> List[TaskResponseSchema]:
        """Получить задачи на конкретный день"""
        try:
            logger.info(
                f"Поиск задач для пользователя {user_id} на дату {date.date()}")

            query = select(TaskModel).where(
                TaskModel.user_id == user_id,
                TaskModel.date == date.date(),
                TaskModel.status == status
            )
            result = self.db_session.execute(query)
            tasks = result.scalars().all()

            if not tasks:
                logger.info(
                    f"Задачи не найдены для пользователя {user_id} на дату {date.date()}")
                return []

            logger.info(
                f"Найдено {len(tasks)} задач для пользователя {user_id} на дату {date.date()}")
            return [
                TaskResponseSchema.model_validate(task) for task in tasks
            ]
        except Exception as e:
            logger.error(
                f"Ошибка при получении задач по дате: {str(e)}", exc_info=True)
            raise

    async def mark_task_completed(self, task_id: str, user_id: str) -> Optional[TaskResponseSchema]:
        """Отметить задачу как выполненную"""
        task = await self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        query = update(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.user_id == user_id
        ).values(
            status="completed",
            updated_at=datetime.now()
        )

        self.db_session.execute(query)
        self.db_session.commit()

        return await self.get_task_by_id(task_id, user_id)


def get_task_service(
    db: Session = Depends(get_db),
) -> TaskService:
    """
    Зависимость для получения Task сервиса
    """
    return TaskService(db)
