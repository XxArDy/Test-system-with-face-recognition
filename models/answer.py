from db import database
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship


class Answer(database.get_base()):
    __tablename__ = 'answers'

    id = Column(Integer, Sequence('answer_id_seq'), primary_key=True, unique=True, nullable=False)
    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    question = relationship("Question", backref="answers")
    
    def __init__(self, text: str, is_correct: bool, question_id: int) -> None:
        self.text = text
        self.is_correct = is_correct
        self.question_id = question_id
    