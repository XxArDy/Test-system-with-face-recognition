from db import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(255), nullable=False)
    is_multiple_choice = Column(Boolean, nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    test = relationship("Test", backref="questions")

    def __init__(self, text: str, is_multiple_choice: bool) -> None:
        self.text = text
        self.is_multiple_choice = is_multiple_choice
