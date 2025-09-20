from fastapi import Response
from config.settings import settings

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    max_age = 3600 * 24 * 7
    
    # Для HTTPS туннелей (loca.lt) нужен samesite='none' для cross-origin запросов
    response.set_cookie(settings.jwt_access_cookie_name, 
                        access_token, 
                        httponly=True,
                        secure=True,  # Обязательно True для HTTPS
                        samesite='none',  # Разрешает cross-origin для туннелей
                        max_age=max_age)
                        
    response.set_cookie(settings.jwt_refresh_cookie_name, 
                        refresh_token, 
                        httponly=True,
                        secure=True,  # Обязательно True для HTTPS
                        samesite='none',  # Разрешает cross-origin для туннелей
                        max_age=max_age)


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.jwt_access_cookie_name, 
                          secure=True,
                          samesite='none')
    response.delete_cookie(settings.jwt_refresh_cookie_name, 
                          secure=True,
                          samesite='none')
