from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, TypeGuard, Union

import jwt
from app import ALGORITHM, SECRET_KEY
from app.data.models import Teacher, TokenData
from app.utils.error import Error
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi import HTTPException

context_pass = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

def verify_password(plain_password, hashed_password):

    return context_pass.verify(plain_password, hashed_password)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(0)
    try:
        print(1)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        print(2)
    except:
        raise Error.UNAUTHORIZED_INVALID
    
    user = await Teacher.find_one(Teacher.login == token_data.username)
    if user is None:
        raise Error.UNAUTHORIZED_INVALID
    
    return user