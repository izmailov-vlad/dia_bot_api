from fastapi import APIRouter, Depends, HTTPException

from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.service.gpt.gpt_service import GPTService
from dependencies import get_gpt_service

router = APIRouter(tags=["gpt"])


@router.post("/gpt")
async def send_message(
    chat_request: ChatGptRequestSchema,
    gpt_service: GPTService = Depends(get_gpt_service),
):
    try:
        response = await gpt_service.request(chat_request)
        return response
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))
