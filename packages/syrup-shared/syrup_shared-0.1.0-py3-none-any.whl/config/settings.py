from typing import List
from pydantic_settings import BaseSettings

class LoggingSettings(BaseSettings):
    log_dir: str = "logs"
    log_file: str = "app.log"
    
    class Config:
        env_prefix = "LOG_"

class AppSettings(BaseSettings):
    app_name: str = "Syrup Chat API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_prefix = "APP_"

class DatabaseSettings(BaseSettings):
    user_database_url: str = "sqlite+aiosqlite:///./user_service.db"
    social_database_url: str = "sqlite+aiosqlite:///./social_service.db"
    content_database_url: str = "sqlite+aiosqlite:///./content_service.db"
    interaction_database_url: str = "sqlite+aiosqlite:///./interaction_service.db"
    chat_database_url: str = "sqlite+aiosqlite:///./chat_service.db"
    
    class Config:
        env_prefix = "DB_"

class JWTSettings(BaseSettings):
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"
    
    class Config:
        env_prefix = "JWT_"

class CORSSettings(BaseSettings):
    origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://myprojectfrontend.loca.lt"
    ]
    allow_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}|.*\.loca\.lt|.*\.ngrok\.io|.*\.trycloudflare\.com)(:\d+)?(/.*)?$"
    
    class Config:
        env_prefix = "CORS_"

class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"
    enabled: bool = True
    score_refresh_seconds: int = 300
    
    class Config:
        env_prefix = "REDIS_"

class S3Settings(BaseSettings):
    access_key_id: str = "f55abbf2689e48a7a5c0682250228bf5"
    secret_access_key: str = "c9a013b509114a2ebcc429ee9cefce71"
    bucket_name: str = "test-backet-syrup"
    region: str = "ru-7"
    endpoint_url: str = "https://s3.ru-7.storage.selcloud.ru"
    use_ssl: bool = True
    verify_ssl: bool = False
    ca_bundle_path: str | None = None
    
    class Config:
        env_prefix = "S3_"

class FileUploadSettings(BaseSettings):
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "video/mp4", "video/webm", "video/ogg",
        "audio/mpeg", "audio/wav", "audio/ogg",
        "application/pdf", "text/plain"
    ]
    
    class Config:
        env_prefix = "FILE_"

class Settings(BaseSettings):
    logging: LoggingSettings = LoggingSettings()
    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    cors: CORSSettings = CORSSettings()
    redis: RedisSettings = RedisSettings()
    s3: S3Settings = S3Settings()
    file_upload: FileUploadSettings = FileUploadSettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""
        extra = "ignore"

settings = Settings()
