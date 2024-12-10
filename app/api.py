"""
Модуль для определения маршрутов API с использованием FastAPI.

Этот модуль предоставляет маршруты для работы с задачами (создание, чтение, обновление, удаление)
и использует зависимости для аутентификации пользователя.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session

from app.dependencies import get_db
from . import crud, schemas, models

# Создание объекта APIRouter
api_router = APIRouter()


def get_current_user(
    session_token: str | None = Cookie(None),  # Токен сессии из cookie
    db: Session = Depends(get_db)  # Сессия базы данных
) -> models.User:
    """
    Получает текущего пользователя на основе токена сессии.

    Если токен сессии отсутствует или сессия истекла, выбрасывает исключение HTTP 401.

    Args:
        session_token (str | None): Токен сессии, переданный через cookie. По умолчанию None.
        db (Session): Сессия базы данных, полученная через зависимость `get_db`.

    Returns:
        models.User: Объект пользователя, если сессия действительна.

    Raises:
        HTTPException: Если пользователь не аутентифицирован или сессия истекла.
    """
    if session_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session: models.Session | None = crud.get_session(db, session_token)
    if session is None or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return session.user


@api_router.get("/tasks", response_model=list[schemas.Task])
async def get_tasks(
    current_user: models.User = Depends(get_current_user),  # Текущий пользователь
    db: Session = Depends(get_db)  # Сессия базы данных
) -> list[schemas.Task]:
    """
    Получает список задач текущего пользователя.

    Args:
        current_user (models.User): Текущий пользователь, полученный через зависимость `get_current_user`.
        db (Session): Сессия базы данных, полученная через зависимость `get_db`.

    Returns:
        list[schemas.Task]: Список задач текущего пользователя.
    """
    tasks: list[models.Task] = crud.get_tasks(db, user_id=current_user.id)
    return tasks


@api_router.post("/tasks", response_model=schemas.Task)
async def create_task(
    task: schemas.TaskCreate,  # Данные для создания задачи
    current_user: models.User = Depends(get_current_user),  # Текущий пользователь
    db: Session = Depends(get_db)  # Сессия базы данных
) -> schemas.Task:
    """
    Создает новую задачу для текущего пользователя.

    Args:
        task (schemas.TaskCreate): Данные для создания задачи.
        current_user (models.User): Текущий пользователь, полученный через зависимость `get_current_user`.
        db (Session): Сессия базы данных, полученная через зависимость `get_db`.

    Returns:
        schemas.Task: Созданная задача.
    """
    db_task: models.Task = crud.create_task(db, task, user_id=current_user.id)
    return db_task


@api_router.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(
    task_id: int,  # Идентификатор задачи
    task: schemas.TaskCreate,  # Данные для обновления задачи
    current_user: models.User = Depends(get_current_user),  # Текущий пользователь
    db: Session = Depends(get_db)  # Сессия базы данных
) -> schemas.Task:
    """
    Обновляет задачу по её идентификатору.

    Если задача не принадлежит текущему пользователю, выбрасывает исключение HTTP 403.

    Args:
        task_id (int): Идентификатор задачи.
        task (schemas.TaskCreate): Данные для обновления задачи.
        current_user (models.User): Текущий пользователь, полученный через зависимость `get_current_user`.
        db (Session): Сессия базы данных, полученная через зависимость `get_db`.

    Returns:
        schemas.Task: Обновленная задача.

    Raises:
        HTTPException: Если задача не найдена или не принадлежит текущему пользователю.
    """
    existing_task: models.Task | None = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    updated_task: models.Task = crud.update_task(db, task_id, task)
    return updated_task


@api_router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(
    task_id: int,  # Идентификатор задачи
    current_user: models.User = Depends(get_current_user),  # Текущий пользователь
    db: Session = Depends(get_db)  # Сессия базы данных
) -> dict[str, str]:
    """
    Удаляет задачу по её идентификатору.

    Если задача не принадлежит текущему пользователю, выбрасывает исключение HTTP 403.

    Args:
        task_id (int): Идентификатор задачи.
        current_user (models.User): Текущий пользователь, полученный через зависимость `get_current_user`.
        db (Session): Сессия базы данных, полученная через зависимость `get_db`.

    Returns:
        dict[str, str]: Сообщение об успешном удалении задачи.

    Raises:
        HTTPException: Если задача не найдена или не принадлежит текущему пользователю.
    """
    existing_task: models.Task | None = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    crud.delete_task(db, task_id)
    return {"message": "Task deleted successfully"}
