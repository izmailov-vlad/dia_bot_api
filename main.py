from fastapi import FastAPI

from api.schemas.chat_gpt_request_schema import ChatGptRequestSchema
from api.service.chat_gpt_service import ChatGPTService
from database.database import Base, engine


# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI приложения
app = FastAPI()


@app.post("/api/gpt")
async def send_message(chat_request: ChatGptRequestSchema):
    try:
        response = await ChatGPTService().send_message(chat_request)

        return response

    except Exception as e:
        print("Error: ", e)


# Точка входа для запуска приложения (если требуется запуск локально)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
