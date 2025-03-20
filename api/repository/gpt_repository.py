import json
import logging
from api.schemas.task.task_schema_create import TaskSchemaCreate
from api.schemas.task.task_schema_response import TaskSchemaResponse
from api.service.gpt.gpt_service import GPTService
from api.service.task.task_service import TaskService
from api.service.smart_tag_service import SmartTagService


# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)


class GPTRepository:
    def __init__(
        self,
        gpt_service: GPTService,
        task_service: TaskService,
        smart_tag_service: SmartTagService,
    ):
        self.gpt_service = gpt_service
        self.task_service = task_service
        self.smart_tag_service = smart_tag_service
        logger.debug("GPTRepository инициализирован с сервисами")

    async def request(self, request: str):
        logger.debug(f"Получен запрос GPT: {request}")

        try:
            response = await self.gpt_service.request(request)
            logger.debug(f"Получен ответ от GPT-сервиса: {response}")

            if (response.choices[0].message.tool_calls == None):
                logger.debug(
                    "В ответе нет вызовов инструментов, возвращаем обычное сообщение")
                return {"message": response.choices[0].message.content}

            result = None
            for tool_call in response.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                logger.debug(
                    f"Обрабатываем вызов инструмента: {name} с аргументами: {args}")

                try:
                    result = await self._call_function(name, args)
                    logger.debug(
                        f"Результат вызова инструмента {name}: {result}")
                except Exception as e:
                    logger.error(
                        f"Ошибка при вызове инструмента {name}: {str(e)}", exc_info=True)
                    raise

            return result
        except Exception as e:
            logger.error(f"Ошибка в методе request: {str(e)}", exc_info=True)
            raise

    # [request] field is a string from args
    async def create_task_tool(self, request: str) -> TaskSchemaResponse:
        logger.debug(f"Вызов create_task_tool с запросом: {request}")

        try:
            taskSchemaResponseGpt = await self.task_service.create_task_gpt(request)
            logger.debug(f"Результат create_task_gpt: {taskSchemaResponseGpt}")

            task_data = TaskSchemaCreate(
                title=taskSchemaResponseGpt.title,
                start_time=taskSchemaResponseGpt.start_time,
                end_time=taskSchemaResponseGpt.end_time
            )
            logger.debug(f"Создаем задачу с данными: {task_data}")

            taskSchemaResponse = await self.task_service.create_task(task=task_data)
            logger.debug(f"Задача успешно создана: {taskSchemaResponse}")

            return taskSchemaResponse
        except Exception as e:
            logger.error(
                f"Ошибка в методе create_task_tool: {str(e)}", exc_info=True)
            raise

    async def _call_function(self, name, args):
        logger.debug(f"Приватный вызов _call_function: {name}, args: {args}")

        try:
            if name == "create_task_tool":
                logger.debug("Обработка инструмента create_task_tool")
                task = await self.create_task_tool(**args)
                logger.debug(f"Результат create_task_tool: {task}")
                return {"task": task}
            else:
                logger.warning(f"Неизвестный инструмент: {name}")
                return {"error": f"Неизвестный инструмент: {name}"}
        except Exception as e:
            logger.error(
                f"Ошибка в методе _call_function для {name}: {str(e)}", exc_info=True)
            raise
