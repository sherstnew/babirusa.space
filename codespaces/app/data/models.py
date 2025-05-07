from beanie import Document

class User(Document):
    username: str
    password: str

class UserPort(Document):
    username: str
    port: int