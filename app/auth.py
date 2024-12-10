"""
Модуль для работы с паролями и их хэшированием с использованием библиотеки bcrypt.

Этот модуль предоставляет функции для проверки пароля и генерации хэша пароля.
"""

import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли обычный пароль его хэшированной версии.

    Args:
        plain_password (str): Обычный пароль, введенный пользователем.
        hashed_password (str): Хэшированный пароль, сохраненный в базе данных.

    Returns:
        bool: True, если пароль совпадает с хэшированной версией, иначе False.
    """
    result: bool = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    return result


def get_password_hash(password: str) -> str:
    """
    Генерирует хэш пароля с использованием библиотеки bcrypt.

    Args:
        password (str): Обычный пароль, который нужно хэшировать.

    Returns:
        str: Хэшированный пароль в виде строки.
    """
    salt: bytes = bcrypt.gensalt()
    hashed_password: bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')
