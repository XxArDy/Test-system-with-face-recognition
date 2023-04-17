from db import database
from sqlalchemy import Column, String, Integer, Sequence


class Subject(database.get_base()):
    __tablename__ = 'subjects'

    id = Column(Integer, Sequence('subject_id_seq'), primary_key=True, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    
    def __init__(self, name: str) -> None:
        self.name = name
