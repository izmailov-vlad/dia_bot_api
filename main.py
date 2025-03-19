from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.gpt_routes import router as gpt_router
from api.routes.task_routes import router as task_router
from database.database import Base, engine


# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI приложения
app = FastAPI(title="Task Management API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(gpt_router, prefix="/api")
app.include_router(task_router, prefix="/api")

# Точка входа для запуска приложения (если требуется запуск локально)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
