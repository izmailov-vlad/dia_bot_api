from openai import OpenAI
from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.service.smart_tag_service import SmartTagService
from api.service.task.task_service import TaskService
from api.service.gpt.gpt_system_prompt import system_prompt


class GPTService:
    def __init__(
        self,
        client: OpenAI,
        task_service: TaskService,
        smart_tag_service: SmartTagService,
    ):
        self.client = client
        self.task_service = task_service
        self.smart_tag_service = smart_tag_service

    async def request(self, request: ChatGptRequestSchema):
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
