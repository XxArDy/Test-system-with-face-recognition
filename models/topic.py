from db import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    subject = relationship("Subject", backref="topics")
    
    def __init__(self, name: str) -> None:
        self.name = name
    