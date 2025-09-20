# SYRUP Shared Library

Общая библиотека компонентов для всех микросервисов SYRUP.

## 📁 Структура

```
shared/
├── config/          # Конфигурация
│   ├── __init__.py
│   └── settings.py  # Настройки приложения
├── database/        # База данных
│   ├── __init__.py
│   ├── connection.py    # Подключение к БД
│   ├── models.py        # SQLAlchemy модели
│   └── managers.py      # Менеджеры для работы с БД
├── schemas/         # Pydantic схемы
│   ├── __init__.py
│   ├── user.py          # Схемы пользователей
│   ├── role.py          # Схемы ролей
│   ├── token.py         # Схемы токенов
│   ├── history.py       # Схемы историй
│   ├── comment.py       # Схемы комментариев
│   ├── like.py          # Схемы лайков
│   ├── followers.py     # Схемы подписок
│   ├── friends.py       # Схемы друзей
│   ├── message.py       # Схемы сообщений
│   ├── media.py         # Схемы медиа
│   └── response.py      # Общие схемы ответов
└── utils/           # Утилиты
    ├── __init__.py
    ├── logger.py        # Логирование
    ├── jwt.py           # JWT токены
    ├── cookie.py        # Работа с cookies
    ├── json_utils.py    # JSON утилиты
    ├── validation.py    # Валидация
    └── file_utils.py    # Работа с файлами
```

## 🚀 Использование

### Импорт компонентов

```python
# Конфигурация
from shared.config import settings
from shared.config import (
    Settings, LoggingSettings, AppSettings, DatabaseSettings,
    JWTSettings, CORSSettings, RedisSettings, S3Settings, FileUploadSettings
)

# База данных
from shared.database import get_engine, get_session_maker, Base
from shared.database.models import User, History, Comment
from shared.database.managers import UserManager, HistoryManager

# Схемы
from shared.schemas import UserCreate, UserOut, HistoryCreate, HistoryOut

# Утилиты
from shared.utils import (
    app_logger, 
    create_access_token, 
    validate_password,
    generate_unique_filename
)
```

### Работа с базой данных

```python
from shared.database import get_session_maker
from shared.database.models import User
from shared.database.managers import UserManager

# Получение сессии для конкретного сервиса
SessionLocal = get_session_maker("user")
async with SessionLocal() as session:
    user_manager = UserManager(session)
    
    # Создание пользователя
    user = await user_manager.create(User, login="test", password_hash="hash")
    
    # Получение пользователя
    user = await user_manager.get_by_login("test")
```

### Работа с JWT

```python
from shared.utils import create_access_token, create_refresh_token, decode_token

# Создание токенов
access_token = create_access_token({"sub": "user_id"})
refresh_token = create_refresh_token({"sub": "user_id"})

# Декодирование токена
try:
    payload = decode_token(access_token)
    user_id = payload["sub"]
except InvalidTokenError as e:
    print(f"Ошибка токена: {e}")
```

### Валидация данных

```python
from shared.utils import validate_password, validate_username, validate_email

# Валидация пароля
password_result = validate_password("mypassword")
if not password_result["is_valid"]:
    print(password_result["errors"])

# Валидация имени пользователя
username_result = validate_username("test_user")
if not username_result["is_valid"]:
    print(username_result["errors"])
```

### Работа с файлами

```python
from shared.utils import (
    generate_unique_filename, 
    is_image_file, 
    format_file_size,
    get_file_mime_type
)

# Генерация уникального имени файла
unique_name = generate_unique_filename("photo.jpg")

# Проверка типа файла
if is_image_file("photo.jpg"):
    print("Это изображение")

# Форматирование размера файла
size_str = format_file_size(1024000)  # "1000.0 KB"

# Получение MIME типа
mime_type = get_file_mime_type("photo.jpg")  # "image/jpeg"
```

## 🔧 Конфигурация

Все настройки находятся в `config/settings.py` и разделены по категориям:

### Структура настроек

```python
from shared.config import settings

# Основные настройки приложения
app_name = settings.app.app_name
debug = settings.app.debug
host = settings.app.host
port = settings.app.port

# Настройки базы данных
user_db_url = settings.database.user_database_url
social_db_url = settings.database.social_database_url

# JWT настройки
secret_key = settings.jwt.secret_key
token_expire_minutes = settings.jwt.access_token_expire_minutes

# Redis настройки
redis_url = settings.redis.url
redis_enabled = settings.redis.enabled

# S3 настройки
s3_bucket = settings.s3.bucket_name
s3_region = settings.s3.region

# Настройки логирования
log_dir = settings.logging.log_dir
log_file = settings.logging.log_file

# CORS настройки
cors_origins = settings.cors.origins

# Настройки загрузки файлов
max_file_size = settings.file_upload.max_file_size
allowed_types = settings.file_upload.allowed_file_types
```

### Обратная совместимость

Старый способ доступа к настройкам по-прежнему работает:

```python
from shared.config import settings

# Старый способ (по-прежнему работает)
user_db_url = settings.user_database_url
secret_key = settings.jwt_secret_key
s3_bucket = settings.s3_bucket_name
```

### Создание собственных настроек

```python
from shared.config import AppSettings

# Создание собственных настроек приложения
class MyAppSettings(AppSettings):
    custom_setting: str = "default_value"
    
    class Config:
        env_prefix = "MY_APP_"

# Использование
my_settings = MyAppSettings()
print(my_settings.custom_setting)  # Читает из MY_APP_CUSTOM_SETTING
```

## 📊 Модели базы данных

### User
- `id` - ID пользователя
- `login` - Логин
- `password_hash` - Хеш пароля
- `role` - Роль пользователя
- `avatar_key` - Ключ аватара
- `about` - О пользователе
- `created_at` - Дата создания
- `updated_at` - Дата обновления

### History
- `id` - ID истории
- `title` - Заголовок
- `description` - Описание
- `author_id` - ID автора
- `created_at` - Дата создания
- `updated_at` - Дата обновления

### Comment
- `id` - ID комментария
- `content` - Содержимое
- `user_id` - ID пользователя
- `history_id` - ID истории
- `comment_type` - Тип комментария
- `comment_metadata` - Метаданные
- `created_at` - Дата создания
- `updated_at` - Дата обновления

## 🛠️ Менеджеры базы данных

### UserManager
- `get_by_login(login)` - Получить пользователя по логину
- `get_by_role(role)` - Получить пользователей по роли
- `create(**kwargs)` - Создать пользователя
- `get_by_id(id)` - Получить по ID
- `update(id, **kwargs)` - Обновить
- `delete(id)` - Удалить

### HistoryManager
- `get_by_author(author_id)` - Получить истории автора
- `get_with_likes_dislikes(history_id)` - Получить с лайками/дизлайками

### LikeManager
- `get_likes_count(history_id)` - Количество лайков
- `get_dislikes_count(history_id)` - Количество дизлайков
- `user_liked(user_id, history_id)` - Проверить лайк
- `user_disliked(user_id, history_id)` - Проверить дизлайк

## 🔒 Безопасность

- JWT токены с настраиваемым временем жизни
- Валидация паролей с требованиями к сложности
- Санитизация пользовательского ввода
- Безопасная работа с файлами

## 📝 Логирование

```python
from shared.utils import app_logger

# Обычное логирование
app_logger.info("Пользователь создан")
app_logger.error("Ошибка при создании пользователя")

# Структурированное логирование
app_logger.info_event("user_created", user_id=123, login="test")
app_logger.error_event("user_creation_failed", error="validation_error")
```

## 🧪 Тестирование

Shared библиотека включает утилиты для тестирования:

```python
from shared.utils import validate_model_data
from shared.schemas import UserCreate

# Валидация данных модели
result = validate_model_data(UserCreate, {"login": "test", "password": "123456"})
if result["is_valid"]:
    print("Данные валидны")
else:
    print("Ошибки:", result["errors"])
```
