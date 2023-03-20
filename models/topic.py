from db import database
from sqlalchemy import Column, String, Integer, ForeignKey, Sequence
from sqlalchemy.orm import relationship


class Topic(database.get_base()):
    __tablename__ = 'topics'

    id = Column(Integer, Sequence('topic_id_seq'), primary_key=True, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    subject = relationship("Subject", backref="topics")
    
    def __init__(self,subject_id: int, name: str) -> None:
        self.name = name
        self.subject_id = subject_id
    