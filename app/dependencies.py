from datetime import datetime
from typing import Generator, Optional

from fastapi import Depends, Cookie
from sqlalchemy.orm import Session

from . import crud, models
from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(session_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)) -> Optional[models.User]:
    if session_token is None:
        return None

    session: Optional[models.Session] = crud.get_session(db, session_token)
    if session is None or session.expires_at < datetime.utcnow():
        return None

    return session.user
