from datetime import datetime


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
    "title": { "type": "string" },  
    "start_time": { "type": "string", "format": "date-time" },
    "end_time": { "type": "string", "format": "date-time" },
  },
  "required": [
    "title",
    "start_time",
    "end_time",
  ],
  "additionalProperties": false
}
"""
