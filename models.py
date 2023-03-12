import uuid
from sqlalchemy import Column, String, Boolean
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    sur_name = Column(String(50))
    path_to_image = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "sur_name": self.sur_name,
            "path_to_image": self.path_to_image,
            "is_active": self.is_active,
        }
