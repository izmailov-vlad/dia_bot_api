import json
from fastapi import Depends
from openai import OpenAI
from api.service.intent_service.intent_service_prompt import intent_service_prompt
from api.schemas.intent.intent_service_response_schema import IntentServiceResponseSchema
from api.service.gpt.gpt_service import get_open_ai_client


class IntentService:
    def __init__(self, client: OpenAI):
        self.client = client

    async def get_intent(self, request: str) -> IntentServiceResponseSchema:
        result = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": intent_service_prompt,
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

        return IntentServiceResponseSchema(**json.loads(result.choices[0].message.content))


def get_intent_service(client: OpenAI = Depends(get_open_ai_client)) -> IntentService:
    return IntentService(client)
