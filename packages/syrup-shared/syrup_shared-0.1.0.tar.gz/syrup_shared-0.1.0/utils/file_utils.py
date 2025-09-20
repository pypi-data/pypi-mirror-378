import os
import uuid
from typing import Optional
from pathlib import Path

def generate_unique_filename(original_filename: str) -> str:
    """Генерирует уникальное имя файла"""
    if not original_filename:
        return str(uuid.uuid4())
    
    file_extension = Path(original_filename).suffix
    unique_name = str(uuid.uuid4())
    return f"{unique_name}{file_extension}"

def get_file_extension(filename: str) -> str:
    """Получает расширение файла"""
    return Path(filename).suffix.lower()

def is_image_file(filename: str) -> bool:
    """Проверяет, является ли файл изображением"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
    return get_file_extension(filename) in image_extensions

def is_video_file(filename: str) -> bool:
    """Проверяет, является ли файл видео"""
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
    return get_file_extension(filename) in video_extensions

def is_audio_file(filename: str) -> bool:
    """Проверяет, является ли файл аудио"""
    audio_extensions = {'.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a'}
    return get_file_extension(filename) in audio_extensions

def get_file_type(filename: str) -> str:
    """Определяет тип файла"""
    if is_image_file(filename):
        return 'image'
    elif is_video_file(filename):
        return 'video'
    elif is_audio_file(filename):
        return 'audio'
    else:
        return 'document'

def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def ensure_directory_exists(directory_path: str) -> bool:
    """Создает директорию, если она не существует"""
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def get_safe_filename(filename: str) -> str:
    """Возвращает безопасное имя файла"""
    # Удаляем небезопасные символы
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    safe_filename = "".join(c for c in filename if c in safe_chars)
    
    # Удаляем множественные точки
    safe_filename = re.sub(r'\.+', '.', safe_filename)
    
    # Удаляем точки в начале и конце
    safe_filename = safe_filename.strip('.')
    
    return safe_filename or "file"

def get_file_mime_type(filename: str) -> str:
    """Определяет MIME тип файла"""
    extension = get_file_extension(filename)
    
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }
    
    return mime_types.get(extension, 'application/octet-stream')
