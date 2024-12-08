from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.orm import Session
from . import models, schemas
from typing import List

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password):
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.owner_id == user_id).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()

def create_session(db: Session, user_id: int) -> models.Session:
    session_token = secrets.token_hex(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # Сессия действительна 7 дней
    db_session = models.Session(user_id=user_id, session_token=session_token, expires_at=expires_at)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_token: str) -> models.Session:
    return db.query(models.Session).filter(models.Session.session_token == session_token).first()

def delete_session(db: Session, session_token: str):
    db.query(models.Session).filter(models.Session.session_token == session_token).delete()
    db.commit()

def task_to_dict(task: models.Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "owner_id": task.owner_id
    }

def get_tasks_with_near_deadline(db: Session, user_id: int):
    one_day_from_now = datetime.now(timezone.utc) + timedelta(days=1)
    tasks = db.query(models.Task).filter(
        models.Task.owner_id == user_id,
        models.Task.deadline <= one_day_from_now,
        models.Task.deadline > datetime.now(timezone.utc)
    ).all()
    return [task_to_dict(task) for task in tasks]

def jaccard_index(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def search_tasks(db: Session, user_id: int, query: str, threshold: float = 0.3) -> List[models.Task]:
    query_set = set(query.split())
    tasks = db.query(models.Task).filter(models.Task.owner_id == user_id).all()
    similar_tasks = []

    for task in tasks:
        task_set = set(task.title.split())
        similarity = jaccard_index(query_set, task_set)
        if similarity >= threshold:
            similar_tasks.append((task, similarity))

    # Сортировка по убыванию сходства
    similar_tasks.sort(key=lambda x: x[1], reverse=True)
    return [task[0] for task in similar_tasks]