from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional


class User(BaseModel):
    email: EmailStr
    hashed_password: str = Field(min_length=6, max_length=20)
    first_name: str = Field(min_length=2, max_length=20)
    last_name: str = Field(min_length=2, max_length=20)
    surname: Optional[str] = Field(min_length=2, max_length=20)
    path_to_image: str
    is_active: Optional[bool]