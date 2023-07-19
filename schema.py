from pydantic import BaseModel
from typing import Optional


class CreateUser(BaseModel):
    name: str
    surname: str
    email: str
    password: str

    class Config:
        orm_mode = True


class UserAuth(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class CreatePost(BaseModel):
    title: str
    content: str
    user_id: int

    class Config:
        orm_mode = True


class UpdatePost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    class Config:
        orm_mode = True
