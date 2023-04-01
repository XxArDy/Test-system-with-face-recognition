from db import database
from sqlalchemy import Column, Integer, ForeignKey, Float, String
from sqlalchemy.orm import relationship


class CompletedTest(database.get_base()):
    __tablename__ = 'completed_tests'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    score = Column(Float, nullable=False)
    
    user = relationship('User', backref='completed_tests')
    test = relationship('Test', backref='completed_tests')
    
    def __init__(self, user_id: str, test_id: int, score: float):
        self.user_id = user_id
        self.test_id = test_id
        self.score = score
        