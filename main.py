from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.auth.routes import auth_routes
from api.task.routes import task_routes
from api.user.routes import user_routes
from database.database import Base, engine
from config.logging_config import setup_logging


# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Инициализируем логирование
setup_logging()

# Настройка логирования
# logging.basicConfig(
#     level=logging.DEBUG,  # Для продакшена используйте logging.INFO или logging.WARNING
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("debug.log"),
#         logging.StreamHandler()
#     ]
# )

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
app.include_router(user_routes.router, prefix="/api")
app.include_router(task_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")

# Точка входа для запуска приложения (если требуется запуск локально)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
