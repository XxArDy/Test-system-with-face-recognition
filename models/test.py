from db import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    is_random = Column(Boolean, nullable=False)
    is_multiple_choice = Column(Boolean, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    topic = relationship("Topic", backref="tests")
    
    def __init__(self, name: str, description: str, 
                 is_random: bool, is_multiple_choice: bool) -> None:
        self.name = name
        self.description = description
        self.is_random = is_random
        self.is_multiple_choice = is_multiple_choice
            