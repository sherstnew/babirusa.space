from pydantic import BaseModel
from app.data.models import Group, Teacher
from typing import List, Optional

class RequestTeacher(BaseModel):
    login: str
    password: str
    
class Pupil(BaseModel):
    id: str
    firstname: str
    lastname: str
    groups: Optional[List[Group]]
    
class UserLogIn(BaseModel):
    teacher_token: str
    
class PupilCreate(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
    
class RequestLogInUser(BaseModel):
    login: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class Group(BaseModel):
    id: str
    name: str
    teacher: Teacher
    pupils: Optional[List[Pupil]]