import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from schemas import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db import get_session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional

import models


SECRET_KEY = "14pPK2rdJWVKfaqQvRn1DZu508KunWImLzP04Bxy5A7a9EEnnFo1ItGZlDJI"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

router = APIRouter()

get_password_hash = lambda password: bcrypt_context.hash(password) 
verify_password = lambda plain_password, hashed_password: bcrypt_context.verify(plain_password, hashed_password)

# region Methods

def authenticate_user(email: str, password: str, db: Session) -> models.User:
    user = db.query(models.User)\
        .filter(models.User.email == email)\
        .first()
    if not user:
        raise get_user_exeption()
    if not verify_password(password, user.hashed_password):
        raise get_user_exeption()
    return user 
    

def create_access_token(email: str, user_id: str,
                        expires_delta: Optional[timedelta] = None) -> str:
    encode = {'sub': email, 'id': user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        if email is None or user_id is None:
            raise get_user_exeption()
        return {'email': email, 'id': user_id}
    except JWTError:
        raise get_user_exeption()
# endregion

# region Router

@router.post('/register')
async def register_user(register_user: User, sesssion: Session = Depends(get_session)) -> User:
    user = models.User(register_user.email,  get_password_hash(register_user.hashed_password),
                       register_user.first_name, register_user.last_name,
                       register_user.surname, register_user.path_to_image, register_user.is_active)
    sesssion.add(user)
    return register_user


@router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise token_exeption()
    token = create_access_token(email=user.email,
                                user_id=user.user_id,
                                expires_delta=timedelta(minutes=20))
    return {'token': token}

# endregion

# region Exeptions

get_user_exeption = lambda: HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={'WWW-Authenticate': 'Bearer'})

token_exeption = lambda: HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail="Incorrect email or password",
                                       headers={'WWW-Authenticate': 'Bearer'})

# endregion