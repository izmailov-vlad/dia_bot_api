import json
from fastapi import Depends
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.chat_gpt_request_model import ChatGptRequestModel
from api.schemas.daily_plan_model import DailyPlanModel
from database.database import get_db

base_prompt = """
Ты — персональный менеджер расписания. Твоя задача — помогать пользователю эффективно управлять своим временем. Пользователь может просить тебя:

1. Создание задачи:
- Название задачи определяется из сообщения пользователя автоматически.
- Если пользователь не указывает дату и время, запланировать задачу на весь текущий день (c 00:00 до 23:59).
- Ответ возвращай в формате Task(JsonSchema)
- Не задавай никаких уточняющих вопросов

2. Перенос задачи (Reschedule):
- Уточнять, какую именно задачу нужно перенести.
- Уточнять новое время и/или дату для переноса.
- Проверять, не конфликтует ли новое время (или дата) с другими задачами.

3. Удаление задачи:
- Уточнять, какую задачу нужно удалить.
- Обязательно запрашивать подтверждение удаления.

4. Предоставление списка задач:
- По умолчанию показывать задачи на текущий день.
- Если пользователь просит — предоставить задачи на неделю или месяц.
- При этом возвращать данные в формате Day (JSON Schema), если требуется именно JSON-ответ.

Отслеживание задач по приоритетам и категориям.

Предупреждение о возможных конфликтах в расписании и предложения альтернативных решений.

Общайся с пользователем дружелюбно и ненавязчиво, но всегда держи в фокусе эффективное планирование и управление временем.

Если пользователь хочет получить свое расписание, то ему должен вернуться Day (JsonSchema)

Спецификация json:

Task:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Task",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "startTime": { "type": "string", "format": "date-time" },
    "endTime": { "type": "string", "format": "date-time" },
    "priority": { "type": "string", "enum": ["low", "medium", "high", "critical"] },
    "category": { "type": "string" },
    "status": { "type": "string", "enum": ["planned", "in_progress", "completed", "cancelled"] },
    "location": { "type": "string" },
    "reminders": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "time": { "type": "string", "format": "date-time" },
          "method": { "type": "string", "enum": ["push", "email", "sms"] }
        },
        "required": ["time", "method"]
      }
    },
    "recurrence": {
      "type": "object",
      "properties": {
        "frequency": { "type": "string", "enum": ["daily", "weekly", "monthly", "yearly"] },
        "interval": { "type": "integer", "minimum": 1 },
        "endDate": { "type": "string", "format": "date-time" }
      },
      "required": ["frequency", "interval"]
    },
    "createdAt": { "type": "string", "format": "date-time" },
    "updatedAt": { "type": "string", "format": "date-time" }
  },
  "required": [
    "id",
    "title",
    "startTime",
    "endTime",
    "status",
    "createdAt",
    "updatedAt"
  ],
  "additionalProperties": false
}

Day:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Day",
  "type": "object",
  "properties": {
    "date": {
      "type": "string",
      "format": "date",
      "description": "Дата в формате ГГГГ-ММ-ДД (YYYY-MM-DD)"
    },
    "tasks": {
      "type": "array",
      "description": "Список задач на этот день",
      "items": {
        "$ref": "Task.json"
      }
    },
    "notes": {
      "type": "string",
      "description": "Произвольные заметки к дню (необязательно)"
    }
  },
  "required": [
    "date",
    "tasks"
  ],
  "additionalProperties": false
}

Week:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Week",
  "type": "object",
  "properties": {
    "startDate": {
      "type": "string",
      "format": "date",
      "description": "Дата начала недели в формате YYYY-MM-DD"
    },
    "endDate": {
      "type": "string",
      "format": "date",
      "description": "Дата окончания недели в формате YYYY-MM-DD"
    },
    "days": {
      "type": "array",
      "description": "Массив дней текущей недели",
      "items": {
        "$ref": "Day.json"
      },
      "minItems": 7,
      "maxItems": 7
    },
    "notes": {
      "type": "string",
      "description": "Общие заметки, относящиеся ко всей неделе"
    }
  },
  "required": [
    "startDate",
    "endDate",
    "days"
  ],
  "additionalProperties": false
}
}
"""

create_schedule_prompt = """
\n\n\n### Response Format should be in json and constains only [tasks] fields\ntask :\ntitle (required str),\ndescription (optional str)\nstartAt (required DateTime)\nendAt (required DateTime)\n"
"""


class ChatGPTService:
    def __init__(self):
        self.client = OpenAI(
            api_key="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",
        )

    def call_function(self, name, args):
        print('args: ', args)
        if name == "create_schedule":
            return self.create_schedule(**args)

    async def create_schedule(self, request: str):
        print("create_schedule request: ", request)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": create_schedule_prompt,
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
            response_format={
                "type": "json_object"
            },
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        gpt_response = response.choices[0].message.content
        print("gpt_response: ", gpt_response)

        daily_plan = DailyPlanModel(
            title=gpt_response.title,
            description=gpt_response.description,
            start_time=gpt_response.start_time,
            end_time=gpt_response.end_time
        )

        return gpt_response

    def send_message(self, request: ChatGptRequestModel):
        user_message = request.message
        print("user_message: ", user_message)
        # Отправка запроса в ChatGPT
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": base_prompt,
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_message
                        }
                    ]
                }
            ],
            # tools=[
            #     {
            #         "type": "function",
            #         "function": {
            #             "name": "create_schedule",
            #             "description": "Create a schedule for my tasks",
            #             "parameters": {
            #                 "type": "object",
            #                 "properties": {
            #                     "request": {
            #                         "type": "string",
            #                         "description": "The tasks to create schedule for"
            #                     }
            #                 },
            #                 "additionalProperties": False,
            #                 "required": ["request"]
            #             },
            #             "strict": True
            #         }
            #     }
            # ],
            response_format={
                "type": "text"
            },
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        print("response: ", response)
        print("tool_calls: ", response.choices[0].message.tool_calls)
        if (response.choices[0].message.tool_calls == None):
            return {"message": response.choices[0].message.content}

        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = self.call_function(name, args)

        print("result: ", result)

        return {"message": result}
