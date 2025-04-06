import json
import logging
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import Depends
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from sqlalchemy.future import select
from sqlalchemy import update, delete
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, MatchText

from api.schemas.task.task_create_schema import TaskCreateSchema
from api.schemas.task.task_response_schema import TaskResponseSchema
from api.schemas.task.task_response_gpt_schema import TaskResponseGptSchema
from api.schemas.task.task_update_schema import TaskUpdateSchema
from api.service.task.create_task_prompt import create_task_prompt
from database.database import get_db
from database.models.task.task_model import TaskModel
from sqlalchemy.orm import Session
from openai import OpenAI

from dependencies import get_open_ai_client, get_qdrant_client, get_transformer_model

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)


class TaskService:
    def __init__(
        self,
        db_session: Session,
        client: OpenAI,
        qdrant_client: QdrantClient,
        transformer_model: SentenceTransformer,
    ):
        self.db_session = db_session
        self.client = client
        self.qdrant_client = qdrant_client
        self.transformer_model = transformer_model

    async def search_by_query(self, query: str, user_id: str) -> List[TaskResponseSchema]:
        """Поиск задач по запросу для конкретного пользователя"""

        # Создаем эмбеддинг для запроса
        query_vector = self.transformer_model.encode(query)

        # Ищем по векторному поиску
        results = self.qdrant_client.search(
            collection_name="tasks",
            query_vector=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=10
        )
        for r in results:
            print('r.score: ', r.score)
            print('r.payload: ', r.payload)
        # Находим результат с максимальным score
        max_score_result = max(results, key=lambda x: x.score, default=None)

        # Преобразуем результат в TaskResponseSchema
        tasks = []
        if max_score_result:
            task = TaskResponseSchema(
                id=max_score_result.id,
                title=max_score_result.payload["title"],
                description=max_score_result.payload["description"],
                start_time=max_score_result.payload["start_time"],
                end_time=max_score_result.payload["end_time"],
                reminder=max_score_result.payload["reminder"],
                mark=max_score_result.payload["mark"],
                status=max_score_result.payload["status"],
            )
            tasks.append(task)

        return tasks

    async def generate_task_gpt(self, request: str) -> TaskResponseGptSchema:
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
            task_schema_response_gpt = TaskResponseGptSchema(**task_gpt_data)

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

            # Создаем текст для эмбеддинга из всех параметров задачи
            task_text = f"""
            Название: {new_task.title}
            Описание: {new_task.description}
            Статус: {new_task.status}
            Метка: {new_task.mark}
            Напоминание: {new_task.reminder}
            Время начала: {new_task.start_time}
            Время окончания: {new_task.end_time}
            """

            # Создаем эмбеддинг на основе полного текста задачи
            task_embedding = self.transformer_model.encode(task_text)
            self.qdrant_client.upsert(
                collection_name="tasks",
                points=[
                    {
                        "id": task_id,
                        "vector": task_embedding,
                        "payload": {
                            "title": new_task.title,
                            "description": new_task.description,
                            "start_time": new_task.start_time,
                            "end_time": new_task.end_time,
                            "reminder": new_task.reminder,
                            "mark": new_task.mark,
                            "status": new_task.status,
                            "user_id": user_id,
                        }
                    }
                ]
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
        client: OpenAI = Depends(get_open_ai_client),
        qdrant_client: QdrantClient = Depends(get_qdrant_client),
        transformer_model: SentenceTransformer = Depends(
            get_transformer_model,
    ),
) -> TaskService:
    """
    Зависимость для получения Task сервиса
    """
    return TaskService(db, client, qdrant_client, transformer_model)
