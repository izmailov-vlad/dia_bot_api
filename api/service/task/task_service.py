import json
import logging
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.schemas.task.task_schema_response_gpt import TaskSchemaResponseGpt
from api.service.task.create_task_prompt import create_task_prompt
from database.models.task.task_model import TaskModel
from sqlalchemy.orm import Session
from openai import OpenAI

from database.models.user.user_model import UserModel

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, db_session: Session, client: OpenAI):
        self.db_session = db_session
        self.client = client

    async def create_task_gpt(self, request: str) -> TaskSchemaResponseGpt:
        logger.debug(f"Начало создания задачи через GPT с запросом: {request}")

        try:
            logger.debug("Отправка запроса к модели GPT-4o")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": create_task_prompt,
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": request
                            }
                        ]
                    }
                ],
                response_format={
                    "type": "json_object"
                },
                temperature=0,
                max_completion_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            gpt_response_json = response.choices[0].message.content
            task_gpt_data = json.loads(gpt_response_json)
            task_schema_response_gpt = TaskSchemaResponseGpt(**task_gpt_data)

            return task_schema_response_gpt

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при парсинге JSON ответа от GPT: {str(e)}")
            logger.error(f"Невалидный JSON: {gpt_response_json}")
            raise
        except Exception as e:
            logger.error(
                f"Ошибка при создании задачи через GPT: {str(e)}", exc_info=True)
            raise

    async def create_task(
        self,
        task: TaskSchemaCreate,
    ) -> TaskSchemaResponse:
        """Создать новую задачу"""

        task_id = str(uuid4())
        task = TaskModel(
            id=task_id,
            title=task.title,
            description=task.description,
            start_time=task.start_time,
            end_time=task.end_time,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        return TaskSchemaResponse(
            id=task_id,
            title=task.title,
            description=task.description,
            start_time=task.start_time,
            end_time=task.end_time
        )

    async def get_task_by_id(self, task_id: str) -> Optional[TaskSchemaResponse]:
        """Получить задачу по ID"""

        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.db_session.execute(query)
        task = result.scalars().first()

        return TaskSchemaResponse(
            id=task_id,
            title=task.title,
            description=task.description,
            start_time=task.start_time,
            end_time=task.end_time
        )

    async def get_all_tasks(self) -> List[TaskSchemaResponse]:
        """Получить все задачи"""

        query = select(TaskModel)
        result = await self.db_session.execute(query)
        tasks = result.scalars().all()

        return [
            TaskSchemaResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                start_time=task.start_time,
                end_time=task.end_time
            ) for task in tasks
        ]

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Optional[TaskSchemaResponse]:
        """Обновить задачу"""

        task = await self.get_task_by_id(task_id)
        if not task:
            return None

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if start_time is not None:
            update_data["start_time"] = start_time
        if end_time is not None:
            update_data["end_time"] = end_time

        update_data["updated_at"] = datetime.now()

        query = update(TaskModel).where(
            TaskModel.id == task_id).values(**update_data)

        await self.db_session.execute(query)
        await self.db_session.commit()

        task = await self.get_task_by_id(task_id)

        return TaskSchemaResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            start_time=task.start_time,
            end_time=task.end_time
        )

    async def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""

        task = await self.get_task_by_id(task_id)
        if not task:
            return False

        query = delete(TaskModel).where(TaskModel.id == task_id)
        await self.db_session.execute(query)
        await self.db_session.commit()

        return True

    async def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TaskSchemaResponse]:
        """Получить задачи в заданном временном диапазоне"""

        query = select(TaskModel).where(
            TaskModel.start_time >= start_date,
            TaskModel.end_time <= end_date
        )
        result = await self.db_session.execute(query)
        tasks = result.scalars().all()

        return [
            TaskSchemaResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                start_time=task.start_time,
                end_time=task.end_time
            ) for task in tasks
        ]
