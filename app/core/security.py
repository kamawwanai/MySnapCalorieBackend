# app/core/security.py

from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

from app.core.config import settings

# Настраиваем bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хеширует plain-текст пароля.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Проверяет соответствие plain-пароля и хеша.
    """
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    """
    Генерирует JWT с полем 'sub' = user_id и временем жизни из настроек.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def decode_access_token(token: str) -> int:
    """
    Раскодирует JWT, проверяет подпись и срок, возвращает user_id.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise
    except Exception:
        raise
