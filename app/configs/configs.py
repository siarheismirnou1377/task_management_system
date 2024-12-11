
import os
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '.', 'config.env'))


# Переменные окружения для приложения
APP_HOST: str = os.getenv('APP_HOST')
APP_PORT: int = int(os.getenv('APP_PORT'))


# Переменные окружения для базы данных
DB_LOGIN: str = os.getenv('DB_LOGIN')

DB_PASSWORD: str = os.getenv('DB_PASSWORD')

DB_NAME: str = os.getenv('DB_NAME')

DB_HOST: str = os.getenv('DB_HOST')

DB_PORT: int = os.getenv('DB_PORT')
