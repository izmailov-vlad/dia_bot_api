from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from fastapi import Depends
from sqlalchemy.orm import Session

from api.schemas.smart_tag.smart_tag_schema_create import SmartTagSchemaCreate
from api.schemas.smart_tag.smart_tag_schema_response import SmartTagSchemaResponse
from database.database import get_db
from database.models.smart_tag.smart_tag_model import SmartTagModel


class SmartTagService:
    def __init__(self, db: Session):
        self.db = db

    def update_db(self, db: Session):
        """Обновляет сессию БД для существующего экземпляра сервиса"""
        self.db = db

    def create_smart_tag(
        self,
        smart_tag: SmartTagSchemaCreate,
    ) -> SmartTagSchemaResponse:
        """Создание нового умного тега"""
        smart_tag = SmartTagModel(
            id=str(uuid4()),
            name=smart_tag.name,

            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(smart_tag)
        self.db.commit()
        self.db.refresh(smart_tag)

        return smart_tag

    def get_smart_tag_by_id(self, tag_id: str) -> Optional[SmartTagSchemaResponse]:
        """Получение умного тега по ID"""
        return self.db.query(SmartTagModel).filter(SmartTagModel.id == tag_id).first()

    def get_all_smart_tags_by_user_id(self, user_id: str) -> List[SmartTagSchemaResponse]:
        """Получение всех умных тегов по user_id"""
        return self.db.query(SmartTagModel).filter(SmartTagModel.user_id == user_id).all()

    def update_smart_tag(
        self,
        tag_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[SmartTagSchemaResponse]:
        """Обновление умного тега"""
        tag = self.db.query(SmartTagModel).filter(
            SmartTagModel.id == tag_id).first()
        if not tag:
            return None

        for key, value in update_data.items():
            if value is not None:
                setattr(tag, key, value)

        tag.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(tag)

        return tag

    def delete_smart_tag(self, tag_id: str) -> bool:
        """Удаление умного тега"""
        tag = self.db.query(SmartTagModel).filter(
            SmartTagModel.id == tag_id).first()
        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()

        return True


def get_smart_tag_service(db: Session = Depends(get_db)) -> SmartTagService:
    """
    Зависимость для получения SmartTag сервиса
    """
    return SmartTagService(db)
