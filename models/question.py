from db import database
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship


class Question(database.get_base()):
    __tablename__ = 'questions'

    id = Column(Integer, Sequence('question_id_seq'), primary_key=True, unique=True, nullable=False)
    text = Column(String(255), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    test = relationship("Test", backref="questions")

    def __init__(self, text: str, test_id: int) -> None:
        self.text = text
        self.test_id = test_id
