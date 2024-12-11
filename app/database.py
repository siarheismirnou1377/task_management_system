"""
Модуль для настройки подключения к базе данных PostgreSQL с использованием SQLAlchemy.

Этот модуль создает движок базы данных, фабрику сессий и базовый класс для объявления моделей ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .configs.configs import DB_HOST, DB_LOGIN, DB_PASSWORD, DB_NAME, DB_PORT


# Строка подключения к базе данных PostgreSQL
SQLALCHEMY_DATABASE_URL: str = f"postgresql://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание движка базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)
"""
Движок базы данных, который используется для взаимодействия с PostgreSQL.
"""

# Создание фабрики сессий
SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""
Фабрика сессий для создания объектов сессий SQLAlchemy.
- `autocommit=False`: Отключает автоматическую фиксацию изменений.
- `autoflush=False`: Отключает автоматическую выгрузку данных в базу.
- `bind=engine`: Привязка сессии к созданному движку базы данных.
"""

# Базовый класс для объявления моделей ORM
Base = declarative_base()
"""
Базовый класс, от которого наследуются все модели ORM.
Используется для объявления таблиц и схемы базы данных.
"""
