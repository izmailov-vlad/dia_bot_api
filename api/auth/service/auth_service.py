from typing import Optional, Tuple
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from uuid import uuid4
from fastapi import Depends, HTTPException, status

from database.database import get_db
from database.models.user import UserModel
from database.models.token_model import RefreshToken
from api.auth.schemas.token_schema import TokenSchema
from api.auth.schemas.auth_register_schema import AuthRegisterSchema
from api.auth.schemas.auth_login_schema import AuthLoginSchema

# Константы для JWT
# Используйте переменные окружения в реальном проекте
SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Получение пользователя по email"""
        return self.db_session.query(UserModel).filter(UserModel.email == email).first()

    def register(self, user_data: AuthRegisterSchema) -> TokenSchema:
        """Регистрация нового пользователя"""
        # Проверяем, существует ли пользователь с таким email
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

        # Создаем нового пользователя
        hashed_password = self.get_password_hash(user_data.password)
        user = UserModel(
            id=str(uuid4()),
            email=user_data.email,
            hashed_password=hashed_password
        )

        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Создаем токены для нового пользователя
        tokens = self.create_tokens(user.id)

        return tokens

    def login(self, user_data: AuthLoginSchema) -> TokenSchema:
        """Авторизация пользователя"""
        # Получаем пользователя по email
        user = self.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        # Проверяем пароль
        if not self.verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        # Создаем новые токены
        tokens = self.create_tokens(user.id)

        return tokens

    def create_access_token(self, user_id: str) -> str:
        """Создание access токена"""
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": user_id,
            "exp": expire
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, user_id: str) -> str:
        """Создание refresh токена и сохранение в БД"""
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expires_at = datetime.utcnow() + expires_delta

        # Создаем токен
        token_value = str(uuid4())

        # Сохраняем в БД
        token = RefreshToken(
            id=str(uuid4()),
            token=token_value,
            user_id=user_id,
            expires_at=expires_at
        )

        # Удаляем старые токены того же пользователя
        old_tokens = self.db_session.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).all()

        for old_token in old_tokens:
            self.db_session.delete(old_token)

        self.db_session.add(token)
        self.db_session.commit()

        return token_value

    def create_tokens(self, user_id: str) -> TokenSchema:
        """Создание пары токенов"""
        access_token = self.create_access_token(user_id)
        refresh_token = self.create_refresh_token(user_id)

        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def validate_access_token(self, token: str) -> Optional[str]:
        """Проверка access токена"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            expiry = payload.get("exp")

            if user_id is None or expiry is None:
                return None

            if datetime.fromtimestamp(expiry) < datetime.utcnow():
                return None

            return user_id
        except JWTError:
            return None

    def refresh_tokens(self, refresh_token: str) -> Optional[TokenSchema]:
        """Обновление пары токенов через refresh токен"""
        # Ищем токен в БД
        token_record = self.db_session.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()

        if not token_record or token_record.expires_at < datetime.utcnow():
            return None

        # Создаем новые токены
        new_tokens = self.create_tokens(token_record.user_id)

        # Удаляем старый токен
        self.db_session.delete(token_record)
        self.db_session.commit()

        return new_tokens

    def revoke_tokens(self, user_id: str) -> bool:
        """Отзыв всех refresh токенов пользователя"""
        tokens = self.db_session.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).all()

        for token in tokens:
            self.db_session.delete(token)

        self.db_session.commit()
        return True


def get_auth_service(db_session: Session = Depends(get_db)) -> AuthService:
    """
    Зависимость для получения AuthService
    """
    return AuthService(db_session)
