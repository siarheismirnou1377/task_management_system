from datetime import datetime
from fastapi import Depends, Cookie
from sqlalchemy.orm import Session
from . import crud, models
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(session_token: str = Cookie(None), db: Session = Depends(get_db)) -> models.User:
    if session_token is None:
        return None
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session = crud.get_session(db, session_token)
    if session is None or session.expires_at < datetime.utcnow():
        return None
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return session.user