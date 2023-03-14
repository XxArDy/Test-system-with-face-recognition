from db import Base
from sqlalchemy import Column, String, Integer


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    def __init__(self, name: str) -> None:
        self.name = name
