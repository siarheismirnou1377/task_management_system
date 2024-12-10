import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    result: bool = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    return result

def get_password_hash(password: str) -> str:
    salt: bytes = bcrypt.gensalt()
    hashed_password: bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')
