import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    # Создаем директорию для логов, если её нет
    log_dir = '/app/logs'
    os.makedirs(log_dir, exist_ok=True)

    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Очищаем существующие обработчики
    root_logger.handlers.clear()

    # Добавляем вывод в файл
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3,
        mode='a'  # Режим добавления
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Добавляем вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Устанавливаем уровень логирования для SQLAlchemy
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    # Добавляем тестовое сообщение
    root_logger.info("Логирование инициализировано")
