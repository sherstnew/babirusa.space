from fastapi import HTTPException
from app.utils.security import context_pass
from app.data.models import Teacher, Pupil
from app.data import schemas
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from app.utils.error import Error

import jwt

context_pass = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(request: schemas.RequestTeacher):
    user_exists = await Teacher.find_one(Teacher.login == request.login)
    if user_exists:
        raise Error.LOGIN_EXISTS
    
    hashed_password = context_pass.hash(request.password)
    user = Teacher(
        login=request.login,
        hashed_password=hashed_password,
        pupils=None
    )
    
    await user.create()
    return schemas.RequestTeacher(
        login=request.login,
        password=hashed_password
    )
    
async def create_pupil(request: schemas.PupilCreate):
    pupil_exists = await Pupil.find_one(Pupil.username == request.username)
    if pupil_exists:
        raise Error.LOGIN_EXISTS
    
    hashed_password = context_pass.hash(request.password)
    user = Pupil(
        username=request.username,
        firstname=request.firstname,
        lastname=request.lastname,
        hashed_password=hashed_password,
        groups=None
    )
    
    await user.create()
    return user
    
async def authenticate_user(data: dict, expires_delta):
    access_token = await create_token(data, expires_delta)
    
    return access_token


async def create_token(data: dict, expires_delta: timedelta = None):
    '''
        data: login
    '''
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt


    
