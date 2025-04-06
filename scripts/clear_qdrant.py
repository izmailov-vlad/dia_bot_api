import os
from qdrant_client import QdrantClient
from qdrant_client.http import models


def clear_qdrant():
    """
    Очищает все точки из коллекции tasks в Qdrant
    """
    # Инициализация клиента
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333")
    )

    try:
        # Удаляем все точки из коллекции
        qdrant_client.delete(
            collection_name="tasks",
            points_selector=models.Filter(
                must=[]
            )
        )
        print("✅ Qdrant успешно очищен")

    except Exception as e:
        print(f"❌ Ошибка при очистке Qdrant: {str(e)}")


if __name__ == "__main__":
    clear_qdrant()
