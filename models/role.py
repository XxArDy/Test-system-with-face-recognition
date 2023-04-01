from db import database
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Role(database.get_base()):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    users = relationship('User', back_populates='role')