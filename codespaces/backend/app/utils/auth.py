from fastapi import HTTPException
from app.utils.security import context_pass
from app.data.models import Teacher
from app.data import schemas
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY_USER
from app.utils.error import Error

import jwt

context_pass = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(request: schemas.Teacher):
    print(request.login)
    user_exists = await Teacher.find_one(Teacher.login == request.login)
    if user_exists:
        return Error.LOGIN_EXISTS
    
    hashed_password = context_pass.hash(request.password)
    user = Teacher(
        login=request.login,
        hashed_password=hashed_password
    )
    
    await user.create()
    return schemas.Teacher(
        login=request.login,
        password=hashed_password
    )
    
    
async def authenticate_user(data: dict):
    access_token = await create_token(data)
    
    return access_token


async def create_token(data: dict, expires_delta: timedelta = None):
    '''
        data: email
    '''
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY_USER), algorithm=ALGORITHM)
    return encoded_jwt


    
