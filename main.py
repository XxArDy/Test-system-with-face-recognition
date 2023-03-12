from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import engine, Base, get_session
from schemas import User
import models


app = FastAPI()

# Create database
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root(session: Session = Depends(get_session)):
    users = session.query(models.User).all()
    return {"users": users}

@app.post("/users/")
def create_user(user: User, session: Session = Depends(get_session)):
    db_user = models.User()
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.sur_name = user.sur_name
    db_user.email = user.email
    db_user.hashed_password = user.hashed_password
    db_user.is_active = user.is_active
    db_user.path_to_image = user.path_to_image
    session.add(db_user)
    return db_user
