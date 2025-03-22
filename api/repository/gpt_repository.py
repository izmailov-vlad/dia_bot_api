import logging

from fastapi import Depends
from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.service.gpt.gpt_service import GPTService, get_gpt_service
from api.service.task.task_service import TaskService, get_task_service

from openai.types.chat.chat_completion import ChatCompletion


# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)


class GPTRepository:
    def __init__(
        self,
        gpt_service: GPTService = Depends(get_gpt_service),
        task_service: TaskService = Depends(get_task_service),
    ):
        self.gpt_service = gpt_service
        self.task_service = task_service
        logger.debug("GPTRepository инициализирован с сервисами")

    async def request(self, request: str) -> ChatCompletion:
        logger.debug(f"Получен запрос GPT: {request}")

        try:
            return await self.gpt_service.request(request)

        except Exception as e:
            logger.error(f"Ошибка в методе request: {str(e)}", exc_info=True)
            raise

    # [request] field is a string from args
    async def create_task(self, request: str) -> TaskSchemaResponse:
        try:
            taskSchemaResponseGpt = await self.task_service.generate_task_gpt(request)
            task_data = TaskSchemaCreate(
                title=taskSchemaResponseGpt.title,
                start_time=taskSchemaResponseGpt.start_time,
                end_time=taskSchemaResponseGpt.end_time
            )
            taskSchemaResponse = await self.task_service.create_task(task=task_data)

            return taskSchemaResponse
        except Exception as e:
            logger.error(
                f"Ошибка в методе create_task_tool: {str(e)}", exc_info=True)
            raise

    async def _call_function(self, name, args):
        try:
            if name == "create_task_tool":
                task = await self.create_task(**args)
                return {"task": task}
            else:
                return {"error": f"Неизвестный инструмент: {name}"}
        except Exception as e:
            raise


def get_gpt_repository(
    gpt_service: GPTService = Depends(get_gpt_service),
    task_service: TaskService = Depends(get_task_service),
) -> GPTRepository:
    """
    Зависимость для получения GPT репозитория
    """
    return GPTRepository(gpt_service, task_service)
