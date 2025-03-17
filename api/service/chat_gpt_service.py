from datetime import datetime
from api.schemas.task_schema import TaskSchema
import json
from openai import OpenAI
from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from database.models.task_model import TaskModel


base_prompt = """
Ты — персональный менеджер расписания. Твоя задача — помогать пользователю эффективно управлять своим временем. Пользователь может просить тебя:
Язык ответа - русский.

1. Создание задачи:
- Название задачи определяется из сообщения пользователя автоматически.
- Если пользователь не указывает дату и время, запланировать задачу на весь текущий день (c 00:00 до 23:59).
- Для создания задачи используй функцию create_task.
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

date_time_property = f"Важно: Всегда используй текущую дату и время для создания задач. Никогда не используй прошедшие даты. Текущая дата и время: {datetime.now()}"

create_task_prompt = """
Создай задачу в соответствии с json schema.
Язык ответа - русский.
{date_time_property}

Task(json schema):
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Task",
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "start_time": { "type": "string", "format": "date-time" },
    "end_time": { "type": "string", "format": "date-time" },
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
        "end_date": { "type": "string", "format": "date-time" }
      },
      "required": ["frequency", "interval"]
    }
  },
  "required": [
    "id",
    "title",
    "start_time",
    "end_time",
    "status"
  ],
  "additionalProperties": false
}
"""


class ChatGPTService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.client = OpenAI(
            api_key="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",
        )
        self.db = db

    async def call_function(self, name, args):
        print('args: ', args, 'name: ', name)
        if name == "create_task_tool":
            task = self.create_task_tool(**args)
            print('created task: ', task)
            # Создаем запись в БД
            # db_task = TaskModel(
            #     id=task.id,
            #     user_id="1",
            #     title=task.title,
            #     description=task.description,
            #     start_time=task.start_time,
            #     end_time=task.end_time,
            #     priority=task.priority,
            #     category=task.category,
            #     status=task.status,
            #     location=task.location,
            # )

            # self.db.add(db_task)
            # await self.db.commit()
            # await self.db.refresh(db_task)

            return {"task": task}

    async def send_message(self, request: ChatGptRequestSchema):
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

        print("response: ", response)
        print("tool_calls: ", response.choices[0].message.tool_calls)
        if (response.choices[0].message.tool_calls == None):
            return {"message": response.choices[0].message.content}

        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = await self.call_function(name, args)

        print("result of tool call: ", result)

        return result

    def create_task_tool(self, request: str) -> TaskSchema:
        print("create_task request: ", request)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": create_task_prompt,
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
            temperature=0,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        gpt_response_json = response.choices[0].message.content
        print("gpt_response: ", gpt_response_json)

        task_data = json.loads(gpt_response_json)
        task_schema = TaskSchema(**task_data)

        return task_schema
