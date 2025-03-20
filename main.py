from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.routes.gpt_routes import router as gpt_router
from api.routes.task_routes import router as task_router
from api.routes.smart_tag_routes import router as smart_tag_router
from database.database import Base, engine


# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Для продакшена используйте logging.INFO или logging.WARNING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

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
app.include_router(smart_tag_router, prefix="/api")

# Точка входа для запуска приложения (если требуется запуск локально)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
