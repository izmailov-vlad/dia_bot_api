from typing import Union
from fastapi import Depends
from api.schemas.schedule.edited_schedule_schema import EditedScheduleSchema
from api.schemas.task.task_create_schema import TaskCreateSchema
from api.schemas.task.task_update_schema import TaskUpdateSchema
from api.service.intent_service.intent_service import IntentService, get_intent_service
from api.service.schedule.schedule_service import ScheduleService, get_schedule_service
from api.service.task.task_service import TaskService, get_task_service
import logging

logger = logging.getLogger(__name__)


class AgentManagerRepository:
    def __init__(
        self,
        schedule_service: ScheduleService,
        intent_service: IntentService,
        task_service: TaskService,
    ):
        self.schedule_service = schedule_service
        self.intent_service = intent_service
        self.task_service = task_service

    async def request(self, request: str, user_id: str) -> Union[str, EditedScheduleSchema]:
        logger.debug(f"Получен запрос. User ID: {user_id}, Request: {request}")

        try:
            # Определение интента
            logger.debug("Определение интента запроса")
            intent = await self.intent_service.get_intent(request)
            logger.debug(f"Определен intent: {intent.delegate_to}")

            if intent.delegate_to == "schedule_agent":
                logger.debug("Делегирование запроса schedule_agent")
                edited_schedule_schema = await self.schedule_service.request(request, user_id)
                logger.debug(
                    f"Получена схема расписания с {len(edited_schedule_schema.tasks)} задачами")

                # Обработка каждой задачи
                for task in edited_schedule_schema.tasks:
                    logger.debug(
                        f"Обработка задачи. Action: {task.action}, Task ID: {task.edited_task.id}")

                    if (task.action == "CREATED"):
                        logger.debug(
                            f"Создание новой задачи: {task.edited_task.title}")
                        created_task = await self.task_service.create_task(
                            task=TaskCreateSchema(
                                **task.edited_task.model_dump()),
                            user_id=user_id
                        )
                        logger.debug(f"Задача создана с ID: {created_task.id}")

                    elif (task.action == "UPDATED"):
                        logger.debug(
                            f"Обновление задачи ID: {task.edited_task.id}")
                        updated_task = await self.task_service.update_task(
                            task_id=task.edited_task.id,
                            user_id=user_id,
                            task=TaskUpdateSchema(
                                **task.edited_task.model_dump())
                        )
                        logger.debug(f"Задача обновлена: {updated_task.id}")

                    elif (task.action == "DELETED"):
                        logger.debug(
                            f"Удаление задачи ID: {task.edited_task.id}")
                        success = await self.task_service.delete_task(
                            task_id=task.edited_task.id,
                            user_id=user_id,
                        )
                        logger.debug(f"Задача удалена: {success}")

                    elif (task.action == "READ"):
                        logger.debug(
                            f"Чтение задачи ID: {task.edited_task.id} - никаких действий не требуется")
                        pass

                logger.debug("Все задачи обработаны успешно")
                return edited_schedule_schema

            else:
                logger.warning(f"Неизвестный агент: {intent.delegate_to}")
                return "Unknown agent"

        except Exception as e:
            logger.error(
                f"Ошибка при обработке запроса: {str(e)}", exc_info=True)
            raise


def get_agent_manager_repository(
    schedule_service: ScheduleService = Depends(get_schedule_service),
    intent_service: IntentService = Depends(get_intent_service),
    task_service: TaskService = Depends(get_task_service),
) -> AgentManagerRepository:
    return AgentManagerRepository(schedule_service, intent_service, task_service)
