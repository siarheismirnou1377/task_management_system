"""
Модуль для определения моделей базы данных с использованием SQLAlchemy.

Этот модуль содержит модели для работы с пользователями, задачами и сессиями.
Каждая модель описывает таблицу в базе данных и её связи с другими таблицами.
"""

from typing import List, Optional

from sqlalchemy import Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей ORM.

    Этот класс наследуется от `DeclarativeBase` и используется для объявления
    таблиц и схемы базы данных.
    """
    pass


class User(Base):
    """
    Модель для представления пользователей в системе.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя (первичный ключ).
        username (str): Уникальное имя пользователя.
        hashed_password (str): Хэшированный пароль пользователя.
        tasks (List[Task]): Список задач, принадлежащих пользователю.
        sessions (List[Session]): Список сессий, связанных с пользователем.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    """Уникальный идентификатор пользователя (первичный ключ)."""

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    """Уникальное имя пользователя."""

    hashed_password: Mapped[str] = mapped_column(String)
    """Хэшированный пароль пользователя."""

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="owner")
    """Список задач, принадлежащих пользователю."""

    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="user")
    """Список сессий, связанных с пользователем."""


class Task(Base):
    """
    Модель для представления задач в системе.

    Атрибуты:
        id (int): Уникальный идентификатор задачи (первичный ключ).
        title (str): Заголовок задачи.
        description (str): Описание задачи.
        status (str): Статус задачи (один из: "новая", "в процессе", "завершена").
        priority (str): Приоритет задачи (один из: "низкий", "средний", "высокий").
        deadline (Optional[DateTime]): Срок выполнения задачи (может быть None).
        owner_id (int): Идентификатор пользователя, которому принадлежит задача.
        owner (User): Пользователь, которому принадлежит задача.
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    """Уникальный идентификатор задачи (первичный ключ)."""

    title: Mapped[str] = mapped_column(String, index=True)
    """Заголовок задачи."""

    description: Mapped[str] = mapped_column(String, index=True)
    """Описание задачи."""

    status: Mapped[str] = mapped_column(
        Enum("новая", "в процессе", "завершена", name="status_enum"),
        default="новая"
    )
    """Статус задачи (один из: "новая", "в процессе", "завершена")."""

    priority: Mapped[str] = mapped_column(
        Enum("низкий", "средний", "высокий", name="priority_enum"),
        default="средний"
    )
    """Приоритет задачи (один из: "низкий", "средний", "высокий")."""

    deadline: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    """Срок выполнения задачи (может быть None)."""

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    """Идентификатор пользователя, которому принадлежит задача."""

    owner: Mapped["User"] = relationship("User", back_populates="tasks")
    """Пользователь, которому принадлежит задача."""


class Session(Base):
    """
    Модель для представления сессий пользователей в системе.

    Атрибуты:
        id (int): Уникальный идентификатор сессии (первичный ключ).
        user_id (int): Идентификатор пользователя, связанного с сессией.
        session_token (str): Уникальный токен сессии.
        expires_at (DateTime): Время истечения сессии.
        user (User): Пользователь, связанный с сессией.
    """
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    """Уникальный идентификатор сессии (первичный ключ)."""

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    """Идентификатор пользователя, связанного с сессией."""

    session_token: Mapped[str] = mapped_column(String, unique=True, index=True)
    """Уникальный токен сессии."""

    expires_at: Mapped[DateTime] = mapped_column(DateTime)
    """Время истечения сессии."""

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    """Пользователь, связанный с сессией."""
