import sys
sys.path.append("..")

import uuid
from sqlalchemy import Column, String, Boolean
from db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    surname = Column(String(50))
    path_to_image = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __init__(self, email: str, password: str, first_name: str,
                 last_name: str, surname: str, path_to_image: str, is_active: bool) -> None:
        self.email = email
        self.hashed_password = password
        self.first_name = first_name
        self.last_name = last_name
        self.surname = surname
        self.path_to_image = path_to_image
        self.is_active = is_active
        
    
    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "email": self.email,
            "hashed_password": self.hashed_password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "surname": self.sur_name,
            "path_to_image": self.path_to_image,
            "is_active": self.is_active,
        }
