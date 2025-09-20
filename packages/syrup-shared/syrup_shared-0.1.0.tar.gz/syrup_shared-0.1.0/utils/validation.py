import re
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationError

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """Валидация пароля"""
    errors = []
    
    if len(password) < 6:
        errors.append("Пароль должен содержать минимум 6 символов")
    
    if len(password) > 100:
        errors.append("Пароль не должен превышать 100 символов")
    
    if not re.search(r'[A-Za-z]', password):
        errors.append("Пароль должен содержать хотя бы одну букву")
    
    if not re.search(r'\d', password):
        errors.append("Пароль должен содержать хотя бы одну цифру")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def validate_username(username: str) -> Dict[str, Any]:
    """Валидация имени пользователя"""
    errors = []
    
    if len(username) < 3:
        errors.append("Имя пользователя должно содержать минимум 3 символа")
    
    if len(username) > 50:
        errors.append("Имя пользователя не должно превышать 50 символов")
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append("Имя пользователя может содержать только буквы, цифры и подчеркивания")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Валидация типа файла"""
    if not filename:
        return False
    
    file_extension = filename.split('.')[-1].lower()
    return file_extension in allowed_types

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Валидация размера файла"""
    return file_size <= max_size

def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> Dict[str, Any]:
    """Валидация параметров пагинации"""
    errors = []
    
    if page < 1:
        errors.append("Страница должна быть больше 0")
    
    if per_page < 1:
        errors.append("Количество элементов на странице должно быть больше 0")
    
    if per_page > max_per_page:
        errors.append(f"Количество элементов на странице не должно превышать {max_per_page}")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "page": max(1, page),
        "per_page": min(max_per_page, max(1, per_page))
    }

def validate_model_data(model_class: BaseModel, data: Dict[str, Any]) -> Dict[str, Any]:
    """Валидация данных модели"""
    try:
        validated_data = model_class(**data)
        return {
            "is_valid": True,
            "data": validated_data.dict(),
            "errors": []
        }
    except ValidationError as e:
        return {
            "is_valid": False,
            "data": None,
            "errors": e.errors()
        }

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Очистка строки от потенциально опасных символов"""
    if not text:
        return ""
    
    # Удаляем HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ограничиваем длину
    if len(text) > max_length:
        text = text[:max_length]
    
    return text
