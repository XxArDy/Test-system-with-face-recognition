from db import database
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship


class Test(database.get_base()):
    __tablename__ = 'tests'

    id = Column(Integer, Sequence('test_id_seq'), primary_key=True, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    time_to_complete = Column(Integer, nullable=False)
    is_random = Column(Boolean, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    topic = relationship("Topic", backref="tests")
    
    def __init__(self, name: str, description: str, time_to_complete: int, 
                 is_random: bool, topic_id: int) -> None:
        self.name = name
        self.description = description
        self.is_random = is_random
        self.time_to_complete = time_to_complete
        self.topic_id = topic_id