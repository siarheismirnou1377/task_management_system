"""
Модуль для работы с зависимостями и получения текущего пользователя в FastAPI.

Этот модуль предоставляет функции для получения сессии базы данных и текущего пользователя,
основываясь на токене сессии, переданном через cookie.
"""

from datetime import datetime
from typing import Generator, Optional

from fastapi import Depends, Cookie
from sqlalchemy.orm import Session

from . import crud, models
from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Генератор для получения сессии базы данных.

    Эта функция создает и возвращает сессию базы данных, которая автоматически закрывается после использования.

    Yields:
        Session: Объект сессии базы данных.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    session_token: Optional[str] = Cookie(None),  # Токен сессии из cookie
    db: Session = Depends(get_db)  # Сессия базы данных
) -> Optional[models.User]:
    """
    Получает текущего пользователя на основе токена сессии.

    Эта функция проверяет токен сессии, переданный через cookie, и возвращает объект пользователя,
    если сессия действительна. Если токен отсутствует, сессия недействительна или истек срок её действия,
    возвращается None.

    Args:
        session_token (Optional[str]): Токен сессии, переданный через cookie. По умолчанию None.
        db (Session): Сессия базы данных, полученная через зависимость `get_db`.

    Returns:
        Optional[models.User]: Объект пользователя, если сессия действительна, иначе None.
    """
    if session_token is None:
        return None

    # Получаем сессию по токену
    session: Optional[models.Session] = crud.get_session(db, session_token)

    # Проверяем, что сессия существует и не истек срок её действия
    if session is None or session.expires_at < datetime.utcnow():
        return None

    # Возвращаем пользователя, связанного с сессией
    return session.user
