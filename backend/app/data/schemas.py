from typing import List, Optional

from pydantic import BaseModel


class RequestTeacher(BaseModel):
    login: str
    password: str


class Pupil_(BaseModel):
    id: str
    username: str
    firstname: str
    lastname: str
    container_status: str


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


class PupilPassword(BaseModel):
    password: str


class FileInfo(BaseModel):
    name: str
    relative_path: str
    size: int
    is_directory: bool


class SearchResult(BaseModel):
    relative_path: str
    line_number: int
    line_content: str


class FileContent(BaseModel):
    relative_path: str
    content: str
    size: int


class OperationResult(BaseModel):
    success: bool
    message: str
    relative_path: str


class HomeworkCheckRequest(BaseModel):
    prompt: str
    file_pattern: str
    usernames: List[str]


class PupilReview(BaseModel):
    username: str
    correct: bool
    score: int
    summary: str
    suggestions: str


class HomeworkCheckResponse(BaseModel):
    results: List[PupilReview]

    
class CreateTemplate(BaseModel):
    code: str