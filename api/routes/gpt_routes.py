import json
from fastapi import APIRouter, Depends, HTTPException

from api.middleware.auth_middleware import get_current_user
from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.repository.gpt_repository import GPTRepository, get_gpt_repository
from database.models.user.user_model import UserModel


router = APIRouter(tags=["gpt"])


@router.post("/gpt")
async def send_message(
    chat_request: ChatGptRequestSchema,
    gpt_repository: GPTRepository = Depends(get_gpt_repository),
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
                result = await _call_function(name, args)
            except Exception as e:
                raise

        return result

    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))


async def _call_function(self, name, args):
    try:
        if name == "create_task_tool":
            task = await self.create_task(**args)
            return {"task": task}
        else:
            return {"error": f"Неизвестный инструмент: {name}"}
    except Exception as e:
        raise
