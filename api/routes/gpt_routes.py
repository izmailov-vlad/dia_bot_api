from enum import Enum
import json
import logging
from fastapi import APIRouter, Depends, HTTPException

from api.middleware.auth_middleware import get_current_user
from api.task.repository.task_repository import TaskRepository, get_task_repository
from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.repository.gpt_repository import GPTRepository, get_gpt_repository
from database.models.user.user_model import UserModel


router = APIRouter(tags=["gpt"])

logger = logging.getLogger(__name__)


class ToolCallAction(Enum):
    CREATE_TASK = "create_task_tool"

    @staticmethod
    def get_tool_call_action(name: str) -> "ToolCallAction":
        if name == ToolCallAction.CREATE_TASK.value:
            return ToolCallAction.CREATE_TASK
        else:
            raise ValueError(f"Неизвестный инструмент: {name}")


@router.post("/gpt")
async def send_message(
    chat_request: ChatGptRequestSchema,
    gpt_repository: GPTRepository = Depends(get_gpt_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        response = await gpt_repository.request(chat_request)

        if (response.choices[0].message.tool_calls == None):
            return {"message": response.choices[0].message.content}

        result = None
        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            try:
                tool_call_action = ToolCallAction.get_tool_call_action(name)
                if tool_call_action == ToolCallAction.CREATE_TASK:
                    result = await task_repository.create_task_gpt(**args, user_id=current_user.id)
            except Exception as e:
                raise

        return result

    except Exception as e:
        logger.error(f"Ошибка в методе send_message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
