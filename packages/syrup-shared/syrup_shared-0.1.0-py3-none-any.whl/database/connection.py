import sys
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Добавляем путь к shared модулям
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.settings import settings

# Создаем движки для каждого сервиса
def get_engine(service_name: str):
    database_urls = {
        "user": settings.user_database_url,
        "social": settings.social_database_url,
        "content": settings.content_database_url,
        "interaction": settings.interaction_database_url,
        "chat": settings.chat_database_url
    }
    
    database_url = database_urls.get(service_name, settings.user_database_url)
    
    engine = create_async_engine(
        url=database_url,
        echo=settings.debug,
        pool_pre_ping=True,
    )
    
    return engine

def get_session_maker(service_name: str):
    engine = get_engine(service_name)
    
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False
    )
    
    return AsyncSessionLocal

class Base(DeclarativeBase):
    pass

engines = {
    "user": get_engine("user"),
    "social": get_engine("social"),
    "content": get_engine("content"),
    "interaction": get_engine("interaction"),
    "chat": get_engine("chat")
}

session_makers = {
    "user": get_session_maker("user"),
    "social": get_session_maker("social"),
    "content": get_session_maker("content"),
    "interaction": get_session_maker("interaction"),
    "chat": get_session_maker("chat")
}
