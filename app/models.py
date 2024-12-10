from sqlalchemy import Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from typing import List, Optional


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="owner")
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(Enum("новая", "в процессе", "завершена", name="status_enum"), default="новая")
    priority: Mapped[str] = mapped_column(Enum("низкий", "средний", "высокий", name="priority_enum"), default="средний")
    deadline: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    owner: Mapped["User"] = relationship("User", back_populates="tasks")

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    session_token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship("User", back_populates="sessions")