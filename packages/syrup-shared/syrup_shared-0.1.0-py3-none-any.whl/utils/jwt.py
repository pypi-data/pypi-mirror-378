from typing import Dict
from datetime import datetime, timedelta, timezone
from jose import jwt
from config.settings import settings
from utils.logger import app_logger

class JWTError(Exception):
    """Base JWT exception"""
    pass

class InvalidTokenError(JWTError):
    """Invalid token exception"""
    pass

def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            app_logger.warning(f"В токене отсутствует sub {payload=}")
            raise InvalidTokenError("Неверный токен, отсутствует sub")
        return payload
    except jwt.JWTError as e:
        app_logger.warning(f"Ошибка декодирования токена: {e}")
        raise InvalidTokenError(f"Неверный токен: {e}")
