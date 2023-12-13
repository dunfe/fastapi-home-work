from typing import List, Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[int] = None
    priority: Optional[str] = None


class TaskCreate(TaskBase):
    summary: str
    user_id: int


class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    company_id: Optional[int] = None


class UserCreate(UserBase):
    email: str
    username: str
    password: str
    company_id: str


class User(UserBase):
    id: int
    tasks: List[Task] = []

    class Config:
        orm_mode = True


class CompanyBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    mode: Optional[str] = None
    rating: Optional[str] = None


class CompanyCreate(CompanyBase):
    name: str


class Company(CompanyBase):
    id: int
    users: List[User] = []

    class Config:
        orm_mode = True
