from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class User(BaseModel):
    email: str
    hashed_password: str
    first_name: str
    last_name: str
    sur_name: Optional[str]
    path_to_image: str
    is_active: Optional[bool]