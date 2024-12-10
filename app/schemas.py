from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str
    status: str = "новая"
    priority: str = "средний"
    deadline: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    tasks: List[Task] = []

    class Config:
        from_attributes = True
