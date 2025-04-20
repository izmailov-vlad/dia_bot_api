from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from api.user.schemas.user_schema_response import UserSchemaResponse
from api.user.schemas.user_schmea_request_update import UserSchemaRequestUpdate
from database.database import get_db
from database.models.user.user_model import UserModel


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def update_user(self, user_id: str, user_data: UserSchemaRequestUpdate) -> Optional[UserSchemaResponse]:
        """
        Обновляет данные пользователя
        """
        # Проверяем существование пользователя
        user = self.db_session.query(UserModel).filter(
            UserModel.id == user_id).first()
        if not user:
            return None

        # Формируем данные для обновления
        update_data = user_data.model_dump(exclude_unset=True)

        # Если изменяется email, проверяем его уникальность
        if "email" in update_data:
            existing_user = self.db_session.query(UserModel).filter(
                UserModel.email == update_data["email"],
                UserModel.id != user_id
            ).first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Пользователь с email {update_data['email']} уже существует"
                )

        # Добавляем время обновления
        update_data["updated_at"] = datetime.now()

        # Выполняем обновление
        for key, value in update_data.items():
            setattr(user, key, value)

        self.db_session.commit()
        self.db_session.refresh(user)

        # Возвращаем обновленного пользователя
        return UserSchemaResponse.model_validate(user)

    def delete_user(self, user_id: str) -> bool:
        """
        Удаляет пользователя
        """
        # Проверяем существование пользователя
        user = self.db_session.query(UserModel).filter(
            UserModel.id == user_id).first()
        if not user:
            return False

        # Выполняем удаление
        self.db_session.delete(user)
        self.db_session.commit()

        return True


# Функция для внедрения зависимости
def get_user_service(db_session: Session = Depends(get_db)) -> UserService:
    """
    Возвращает экземпляр UserService для внедрения зависимости.

    Args:
        db_session: Сессия базы данных

    Returns:
        UserService: Сервис для работы с пользователями
    """
    return UserService(db_session)
