from fastapi import Depends
from openai import OpenAI
import json
import logging
from sqlalchemy import and_, or_

from api.schemas.schedule.edited_schedule_schema import EditedScheduleSchema
from api.schemas.schedule.filters_response_schema import TaskFilterSchema
from api.schemas.task.task_response_schema import TaskResponseSchema
from api.service.schedule.edit_schedule_prompt import edit_schedule_prompt
from api.service.schedule.schedule_service_prompt import schedule_service_prompt
from api.service.schedule.define_filters_prompt import define_filters_prompt
from sqlalchemy.orm import Session

from database.database import get_db
from database.models.task.task_model import TaskModel
from dependencies import get_open_ai_client

logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self, client: OpenAI, db_session: Session):
        self.client = client
        self.db_session = db_session

    async def request(self, request: str, user_id: str) -> EditedScheduleSchema:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": schedule_service_prompt,
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
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_tasks_by_user_request",
                        "description": "Get tasks by user request",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "request": {
                                    "type": "string",
                                    "description": "User request for getting tasks"
                                }
                            },
                            "required": ["request"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "edit_schedule",
                        "description": "Edit the schedule",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "request": {
                                    "type": "string",
                                    "description": "The request to edit the schedule",
                                },
                            },
                            "required": ["request"],
                        }
                    }
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        logger.debug(f"Обработка ответа от GPT. User ID: {user_id}")
        logger.debug(f"response: {response}")
        logger.debug(
            f"response.choices[0].message.content: {response.choices[0].message.content}")

        if response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            logger.debug(
                f"Обнаружен вызов функции: {tool_calls[0].function.name}",
            )
            logger.debug(
                f"Аргументы функции: {tool_calls[0].function.arguments}",
            )

            for tool_call in tool_calls:
                if tool_call.function.name == "get_tasks_by_user_request":
                    logger.debug("Выполняется get_tasks_by_user_request")
                    tasks = await self.get_tasks_by_user_request(
                        tool_call.function.arguments,
                        user_id,
                    )
                    logger.debug(f"Получено задач: {len(tasks)}")

                    logger.debug("Передача задач в edit_schedule")
                    schedule_response = await self.edit_schedule(
                        tool_call.function.arguments,
                        tasks,
                    )
                    logger.debug(
                        f"Получен ответ от edit_schedule: {schedule_response}",
                    )
                    return schedule_response

                elif tool_calls[0].function.name == "edit_schedule":
                    logger.debug("Прямой вызов edit_schedule")
                    return await self.edit_schedule(tool_call.function.arguments)
        else:
            logger.debug(
                "Функция не вызвана, выполняется edit_schedule напрямую",
            )
            return await self.edit_schedule(request, user_id)

    async def get_tasks_by_user_request(self, request: str, user_id: str) -> list[TaskResponseSchema]:
        logger.debug(
            f"Получение задач по запросу. User ID: {user_id}, Request: {request}")

        try:
            # Получаем фильтры от GPT
            logger.debug("Отправляем запрос к GPT для получения фильтров")
            filters = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": define_filters_prompt,
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
                response_format={"type": "json_object"},
                temperature=0,
                max_completion_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Логируем ответ GPT
            gpt_response = filters.choices[0].message.content
            logger.debug(f"Получен ответ от GPT: {gpt_response}")

            # Парсим фильтры
            logger.debug("Парсинг фильтров в схему")
            filters_json = json.loads(filters.choices[0].message.content)
            filters_schema = TaskFilterSchema(
                **filters_json["filters"],
            )
            logger.debug(f"Полученные фильтры: {filters_schema}")

            # Формируем запрос к БД
            logger.debug("Формирование запроса к БД с фильтрами")
            tasks = self.db_session.query(TaskModel).filter(
                TaskModel.user_id == user_id,
                # Для start_time
                or_(
                    and_(
                        filters_schema.start_time is not None,
                        filters_schema.start_time.gte is not None,
                        TaskModel.start_time >= filters_schema.start_time.gte
                    ),
                    and_(
                        filters_schema.start_time is not None,
                        filters_schema.start_time.lte is not None,
                        TaskModel.start_time <= filters_schema.start_time.lte
                    )
                ) if filters_schema.start_time else True,
                # Для end_time
                or_(
                    and_(
                        filters_schema.end_time is not None,
                        filters_schema.end_time.gte is not None,
                        TaskModel.end_time >= filters_schema.end_time.gte
                    ),
                    and_(
                        filters_schema.end_time is not None,
                        filters_schema.end_time.lte is not None,
                        TaskModel.end_time <= filters_schema.end_time.lte
                    )
                ) if filters_schema.end_time else True,
                # Для reminder
                or_(
                    and_(
                        filters_schema.reminder is not None,
                        filters_schema.reminder.gte is not None,
                        TaskModel.reminder >= filters_schema.reminder.gte
                    ),
                    and_(
                        filters_schema.reminder is not None,
                        filters_schema.reminder.lte is not None,
                        TaskModel.reminder <= filters_schema.reminder.lte
                    )
                ) if filters_schema.reminder else True,
                # Для mark и status
                TaskModel.mark == filters_schema.mark if filters_schema.mark else True,
                TaskModel.status == filters_schema.status if filters_schema.status else True
            ).all()
            logger.debug(f"Найдено задач: {len(tasks)}")

            # Преобразуем в схему ответа
            response = [TaskResponseSchema(**task.__dict__) for task in tasks]
            logger.debug(f"Задачи успешно преобразованы в схему ответа")

            return response

        except Exception as e:
            logger.error(
                f"Ошибка при получении задач: {str(e)}", exc_info=True)
            raise

    async def edit_schedule(self, request: str, tasks: list[TaskResponseSchema] = None) -> EditedScheduleSchema:
        logger.debug(f"Начало edit_schedule. Request: {request}")
        logger.debug(
            f"Количество переданных задач: {len(tasks) if tasks else 'None'}")

        try:
            # Преобразуем TaskResponseSchema в dict для JSON сериализации
            tasks_json = [task.model_dump_json()
                          for task in tasks] if tasks else None

            # Подготовка данных для запроса
            request_data = {
                "user_request": request,
                "tasks": tasks_json
            }

            json_request = json.dumps(request_data, indent=2)
            logger.debug(f"edit_schedule JSON Request: {json_request}")

            edited_schedule = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": edit_schedule_prompt,
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": json_request
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_completion_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Получение и парсинг ответа
            logger.debug(
                f"edit_schedule Gpt Completion: {edited_schedule}")
            gpt_response = edited_schedule.choices[0].message.content
            logger.debug(f"edit_schedule Gpt Response: {gpt_response}")

            # Преобразование JSON в объект
            logger.debug("Парсинг JSON ответа")
            edited_schedule_json = json.loads(gpt_response)
            logger.debug(f"Распарсенный JSON: {edited_schedule_json}")

            # Создание схемы
            logger.debug("Создание схемы ответа")
            edited_schedule_schema = EditedScheduleSchema(
                **edited_schedule_json,
            )
            logger.debug(f"Схема создана успешно: {edited_schedule_schema}")

            return edited_schedule_schema

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {str(e)}")
            logger.error(f"Проблемный JSON: {gpt_response}")
            raise

        except Exception as e:
            logger.error(f"Ошибка в edit_schedule: {str(e)}", exc_info=True)
            raise


def get_schedule_service(
    client: OpenAI = Depends(get_open_ai_client),
    db_session: Session = Depends(get_db),
) -> ScheduleService:
    return ScheduleService(client, db_session)
