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
