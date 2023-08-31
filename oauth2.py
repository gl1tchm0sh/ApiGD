from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import  HTTPException,status
from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
TOKEN_TIMEOUT = int(settings.TOKEN_TIMEOUT)

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=TOKEN_TIMEOUT)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def validate_access_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        print('Valid Token Parsed')
    except JWTError:
        raise credentials_exception
    
    
if __name__ == '__main__':
    token = create_access_token({'A':'A'})
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate Credentials", headers={"WWW-Authenticate" : "Bearer"})
    validate_access_token(token, credentials_exception)