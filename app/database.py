from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .configs.configs import LOGIN, PASSWORD, DB_NAME


SQLALCHEMY_DATABASE_URL = f"postgresql://{LOGIN}:{PASSWORD}@localhost/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()