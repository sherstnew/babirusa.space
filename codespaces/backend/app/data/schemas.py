from pydantic import BaseModel
from app.data.models import Group
from typing import List, Optional

class Teacher(BaseModel):
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
    firstname: str
    lastname: str
    
class RequestLogInUser(BaseModel):
    login: str
    password: str
    