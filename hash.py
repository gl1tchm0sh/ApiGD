from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(data:str):
    return pwd_context.hash(data)

def verify(plain_key:str, hashed_key):
    return pwd_context.verify(plain_key, hashed_key)