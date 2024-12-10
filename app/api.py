from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session

from app.dependencies import get_db
from . import crud, schemas, models

api_router = APIRouter()

def get_current_user(session_token: str | None = Cookie(None), db: Session = Depends(get_db)) -> models.User:
    if session_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session: models.Session | None = crud.get_session(db, session_token)
    if session is None or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return session.user

@api_router.get("/tasks", response_model=list[schemas.Task])
async def get_tasks(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[schemas.Task]:
    tasks: list[models.Task] = crud.get_tasks(db, user_id=current_user.id)
    return tasks

@api_router.post("/tasks", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> schemas.Task:
    db_task: models.Task = crud.create_task(db, task, user_id=current_user.id)
    return db_task

@api_router.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(task_id: int, task: schemas.TaskCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> schemas.Task:
    existing_task: models.Task | None = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    updated_task: models.Task = crud.update_task(db, task_id, task)
    return updated_task

@api_router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    existing_task: models.Task | None = crud.get_task(db, task_id)
    if existing_task is None or existing_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    crud.delete_task(db, task_id)
    return {"message": "Task deleted successfully"}