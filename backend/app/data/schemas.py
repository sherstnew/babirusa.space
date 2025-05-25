from pydantic import BaseModel
# from app.data.models import Group, Teacher, Pupil
from typing import List, Optional

class RequestTeacher(BaseModel):
    login: str
    password: str
    
class Pupil_(BaseModel):
    id: str
    username: str
    firstname: str
    lastname: str
    
class Teacher_(BaseModel):
    id: str
    login: str
    hashed_password: str 
    pupils: Optional[List[Pupil_]]
    
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
    teacher: Teacher_
    pupils: Optional[List[Pupil_]]
    
class AddPupil(BaseModel):
    group_id: str
    pupil_id: List[str]
    
class RemovePupilsRequest(BaseModel):
    group_id: str
    pupil_id: List[str]
    
class UpdateGroup(BaseModel):
    group_id: str
    new_group_name: str
    