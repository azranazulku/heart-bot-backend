from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    birth_date: date
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    birth_date: date
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
