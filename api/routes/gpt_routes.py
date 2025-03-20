from fastapi import APIRouter, Depends, HTTPException

from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.repository.gpt_repository import GPTRepository
from dependencies import get_gpt_repository

router = APIRouter(tags=["gpt"])


@router.post("/gpt")
async def send_message(
    chat_request: ChatGptRequestSchema,
    gpt_repository: GPTRepository = Depends(get_gpt_repository),
):
    try:
        response = await gpt_repository.request(chat_request)
        return response
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))
