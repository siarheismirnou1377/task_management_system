"""
Модуль для работы с CRUD-операциями (создание, чтение, обновление, удаление) для моделей базы данных.

Этот модуль предоставляет функции для работы с пользователями, задачами и сессиями.
"""

from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from Levenshtein import distance as levenshtein_distance

from . import models, schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Получает пользователя по его идентификатору.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): Идентификатор пользователя.

    Returns:
        Optional[models.User]: Объект пользователя, если найден, иначе None.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Получает пользователя по его имени пользователя.

    Args:
        db (Session): Сессия базы данных.
        username (str): Имя пользователя.

    Returns:
        Optional[models.User]: Объект пользователя, если найден, иначе None.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    """
    Создает нового пользователя.

    Args:
        db (Session): Сессия базы данных.
        user (schemas.UserCreate): Данные для создания пользователя.
        hashed_password (str): Хэшированный пароль пользователя.

    Returns:
        models.User: Созданный объект пользователя.
    """
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: int, hashed_password: str) -> Optional[models.User]:
    """
    Обновляет пароль пользователя.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): Идентификатор пользователя.
        hashed_password (str): Новый хэшированный пароль.

    Returns:
        Optional[models.User]: Обновленный объект пользователя, если найден, иначе None.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.hashed_password = hashed_password
        db.commit()
        db.refresh(user)
    return user


def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Task]:
    """
    Получает список задач пользователя с пагинацией.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): Идентификатор пользователя.
        skip (int): Количество задач для пропуска (пагинация). По умолчанию 0.
        limit (int): Максимальное количество задач для возврата (пагинация). По умолчанию 100.

    Returns:
        List[models.Task]: Список задач пользователя.
    """
    return db.query(models.Task).filter(models.Task.owner_id == user_id).offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskCreate, user_id: int) -> models.Task:
    """
    Создает новую задачу для пользователя.

    Args:
        db (Session): Сессия базы данных.
        task (schemas.TaskCreate): Данные для создания задачи.
        user_id (int): Идентификатор пользователя.

    Returns:
        models.Task: Созданный объект задачи.
    """
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """
    Получает задачу по её идентификатору.

    Args:
        db (Session): Сессия базы данных.
        task_id (int): Идентификатор задачи.

    Returns:
        Optional[models.Task]: Объект задачи, если найден, иначе None.
    """
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task(db: Session, task_id: int, task: schemas.TaskCreate) -> Optional[models.Task]:
    """
    Обновляет задачу.

    Args:
        db (Session): Сессия базы данных.
        task_id (int): Идентификатор задачи.
        task (schemas.TaskCreate): Новые данные для задачи.

    Returns:
        Optional[models.Task]: Обновленный объект задачи, если найден, иначе None.
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        return None

    db_task.title = task.title
    db_task.description = task.description
    db_task.status = task.status
    db_task.priority = task.priority
    db_task.deadline = task.deadline

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    """
    Удаляет задачу по её идентификатору.

    Args:
        db (Session): Сессия базы данных.
        task_id (int): Идентификатор задачи.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()


def create_session(db: Session, user_id: int) -> models.Session:
    """
    Создает новую сессию для пользователя.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): Идентификатор пользователя.

    Returns:
        models.Session: Созданный объект сессии.
    """
    session_token = secrets.token_hex(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    db_session = models.Session(user_id=user_id, session_token=session_token, expires_at=expires_at)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_session(db: Session, session_token: str) -> Optional[models.Session]:
    """
    Получает сессию по её токену.

    Args:
        db (Session): Сессия базы данных.
        session_token (str): Токен сессии.

    Returns:
        Optional[models.Session]: Объект сессии, если найден, иначе None.
    """
    return db.query(models.Session).filter(models.Session.session_token == session_token).first()


def delete_session(db: Session, session_token: str):
    """
    Удаляет сессию по её токену.

    Args:
        db (Session): Сессия базы данных.
        session_token (str): Токен сессии.
    """
    db.query(models.Session).filter(models.Session.session_token == session_token).delete()
    db.commit()


def task_to_dict(task: models.Task) -> dict:
    """
    Преобразует объект задачи в словарь.

    Args:
        task (models.Task): Объект задачи.

    Returns:
        dict: Словарь с данными задачи.
    """
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "owner_id": task.owner_id
    }


def get_tasks_with_near_deadline(db: Session, user_id: int) -> List[dict]:
    """
    Получает список задач пользователя, у которых срок выполнения истекает в течение суток.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): Идентификатор пользователя.

    Returns:
        List[dict]: Список задач в виде словарей.
    """
    one_day_from_now = datetime.now(timezone.utc) + timedelta(days=1)
    tasks = db.query(models.Task).filter(
        models.Task.owner_id == user_id,
        models.Task.deadline <= one_day_from_now,
        models.Task.deadline > datetime.now(timezone.utc)
    ).all()
    return [task_to_dict(task) for task in tasks]


def search_tasks(db: Session, user_id: int, query: str, threshold: int = 5) -> List[models.Task]:
    """
    Ищет задачи пользователя по заголовку с использованием алгоритма Левенштейна.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): Идентификатор пользователя.
        query (str): Поисковый запрос.
        threshold (int): Максимальное расстояние Левенштейна для совпадения. По умолчанию 5.

    Returns:
        List[models.Task]: Список задач, соответствующих запросу.
    """
    tasks = db.query(models.Task).filter(models.Task.owner_id == user_id).all()
    similar_tasks: List[Tuple[models.Task, int]] = []

    for task in tasks:
        distance = levenshtein_distance(query.lower(), task.title.lower())
        if distance <= threshold:
            similar_tasks.append((task, distance))
    similar_tasks.sort(key=lambda x: x[1])
    return [task[0] for task in similar_tasks]