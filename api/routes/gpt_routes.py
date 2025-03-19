from fastapi import APIRouter, HTTPException

from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.service.chat_gpt_service import ChatGPTService

router = APIRouter(tags=["gpt"])


@router.post("/gpt")
async def send_message(chat_request: ChatGptRequestSchema):
    try:
        response = await ChatGPTService().send_message(chat_request)
        return response
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))
