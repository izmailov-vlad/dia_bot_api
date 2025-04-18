from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from api.user.schemas.user_schema_request_create import UserSchemaRequestCreate
from api.user.schemas.user_schema_response import UserSchemaResponse
from api.user.schemas.user_schmea_request_update import UserSchemaRequestUpdate
from database.database import get_db
from database.models.user.user_model import UserModel


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_user(self, user_data: UserSchemaRequestCreate) -> UserSchemaResponse:
        """
        Создает нового пользователя

        Args:
            user_data: Данные для создания пользователя

        Returns:
            UserSchemaResponse: Созданный пользователь

        Raises:
            HTTPException: Если пользователь с таким telegram_id уже существует
        """
        # Проверяем, существует ли пользователь с таким telegram_id
        existing_user = self.db_session.query(UserModel).filter(
            UserModel.telegram_id == user_data.telegram_id).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с telegram_id {user_data.telegram_id} уже существует"
            )

        # Создаем нового пользователя
        user = UserModel(
            id=str(uuid4()),
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        return UserSchemaResponse.model_validate(user)

    def update_user(self, user_id: str, user_data: UserSchemaRequestUpdate) -> Optional[UserSchemaResponse]:
        """
        Обновляет данные пользователя

        Args:
            user_id: ID пользователя
            user_data: Данные для обновления

        Returns:
            Optional[UserSchemaResponse]: Обновленный пользователь или None, если пользователь не найден

        Raises:
            HTTPException: Если при обновлении возникают конфликты (например, telegram_id уже занят)
        """
        # Проверяем существование пользователя
        user = self.db_session.query(UserModel).filter(
            UserModel.id == user_id).first()
        if not user:
            return None

        # Формируем данные для обновления
        update_data = user_data.model_dump(exclude_unset=True)

        # Если изменяется telegram_id, проверяем его уникальность
        if "telegram_id" in update_data:
            existing_user = self.db_session.query(UserModel).filter(
                UserModel.telegram_id == update_data["telegram_id"],
                UserModel.id != user_id
            ).first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Пользователь с telegram_id {update_data['telegram_id']} уже существует"
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

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь был удален, False если пользователь не найден
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
