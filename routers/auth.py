from fastapi import APIRouter, status, HTTPException, Response
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from classes import ConnectionBroker
from hash import verify, hash
import oauth2

router = APIRouter(tags=['Authentication'])

#def authorize(apikey:str, broker=ConnectionBroker()):
@router.post('/authenticate')
def authorize(apikey:str):
    broker = ConnectionBroker()
    query = f"SELECT apikey FROM config where apikey = '{apikey}'"
    hashed_key = broker.execute_query(query)
    hashed_key = hash(hashed_key[0][0]) if len(hashed_key) > 0 else None
    if not hashed_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    if not verify(apikey, hashed_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    access_token = oauth2.create_access_token({"dummy":"dummy data"}) #7:48

    return {"access_token" : access_token, "token_type": "bearer"}

if __name__ == '__main__':
    access_token = authorize('x')
    print(access_token)
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                          detail="Could not Validate Credentials", 
                                          headers={"WWW-Authenticate" : "Bearer"})
    oauth2.validate_access_token(access_token['access_token'], credentials_exception)