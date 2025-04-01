from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.service.task.task_service import TaskService, get_task_service
from api.service.gpt.gpt_system_prompt import system_prompt
from dependencies import get_open_ai_client


class GPTService:
    def __init__(
        self,
        client: OpenAI,
        task_service: TaskService,
    ):
        self.client = client
        self.task_service = task_service

    async def request(self, request: ChatGptRequestSchema) -> ChatCompletion:
        return self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt,
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": request.message
                        }
                    ]
                }
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "create_task_tool",
                        "description": "Create a task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "request": {
                                    "type": "string",
                                    "description": "The task to create"
                                }
                            },
                            "additionalProperties": False,
                            "required": ["request"]
                        },
                        "strict": True
                    }
                }
            ],
            response_format={
                "type": "text"
            },
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )


def get_gpt_service() -> GPTService:
    """
    Зависимость для получения GPT сервиса
    """
    return GPTService(
        client=get_open_ai_client(),
        task_service=get_task_service(),
    )
