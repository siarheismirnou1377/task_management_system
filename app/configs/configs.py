
import os
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '.', 'config.env'))


LOGIN: str = os.getenv('LOGIN')

PASSWORD: str = os.getenv('PASSWORD')

DB_NAME: str = os.getenv('DB_NAME')

HOST: str = os.getenv('HOST')

PORT: int = os.getenv('PORT')
