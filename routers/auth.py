import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

import models
import utils
from db import get_session

SECRET_KEY = "14pPK2rdJWVKfaqQvRn1DZu508KunWImLzP04Bxy5A7a9EEnnFo1ItGZlDJI"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory='templates')

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

router = APIRouter()


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')


def get_password_hash(password: str):
    bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    bcrypt_context.verify(plain_password, hashed_password)


""" Authenticate user """


def authenticate_user(email: str, password: str, db: Session) -> models.User:
    user = db.query(models.User) \
        .filter(models.User.email == email) \
        .first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


""" Generate user token """


def create_access_token(email: str, user_id: str,
                        expires_delta: Optional[timedelta] = None) -> str:
    encode = {'sub': email, 'id': user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


""" Get user by token """


async def get_current_user(request: Request) -> dict:
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return None
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        if email is None or user_id is None:
            logout(request)
        return {'email': email, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")


""" View login form """


@router.get('/login', response_class=HTMLResponse)
async def view_login(request: Request):
    return templates.TemplateResponse('auth/login.html', {'request': request,
                                                          'title': 'Вхід'})


""" View register form """


@router.get('/register', response_class=HTMLResponse)
async def view_register(request: Request):
    return templates.TemplateResponse('auth/register.html', {'request': request,
                                                             'title': 'Реєстрація'})


""" Login and create user token """


@router.post('/login', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_session)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Не вірні данні користувача"
            return templates.TemplateResponse('auth/login.html', {'request': request,
                                                                  'title': 'Вхід',
                                                                  'msg': msg})
        return response
    except HTTPException:
        msg = "Невідома ошибка"
        return templates.TemplateResponse('auth/login.html', {'request': request,
                                                              'title': 'Вхід',
                                                              'msg': msg})


""" Register user and add to database """


@router.post('/register', response_class=HTMLResponse)
async def register(request: Request, email: str = Form(), password: str = Form(),
                   password2: str = Form(), firstname: str = Form(),
                   lastname: str = Form(), img: str = Form(),
                   surname: Optional[str] = Form(),
                   db: Session = Depends(get_session)):
    validation1 = db.query(models.User).filter(models.User.email == email).first()

    if validation1 is not None:
        msg = "Така пошта вже існує"
        return templates.TemplateResponse('auth/register.html', {'request': request,
                                                                 'title': 'Реєстрація',
                                                                 'msg': msg})

    if password != password2:
        msg = "Паролі не співпадають"
        return templates.TemplateResponse('auth/register.html', {'request': request,
                                                                 'title': 'Реєстрація',
                                                                 'msg': msg})

    user_id = uuid.uuid4()

    file_path = f'static/users/images/{user_id}.png'

    utils.save_image_base64(img.split(',')[1], file_path)

    if utils.get_face_count(file_path) <= 0:
        msg = "На фото невидно лиця"
        os.remove(file_path)
        return templates.TemplateResponse('auth/register.html', {'request': request,
                                                                 'title': 'Реєстрація',
                                                                 'msg': msg})

    user = models.User(user_id=user_id, email=email, password=get_password_hash(password),
                       first_name=firstname, last_name=lastname, surname=surname,
                       path_to_image=file_path, is_active=True)
    db.add(user)
    return RedirectResponse(request.url_for('view_login'), status_code=status.HTTP_302_FOUND)


""" Aunhenticate user and add token to cookie """


@router.post('/token')
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_session)) -> bool:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token = create_access_token(email=user.email,
                                user_id=user.user_id,
                                expires_delta=timedelta(minutes=60))

    response.set_cookie(key='access_token', value=token, httponly=True)

    return True


""" Logout user """


@router.get('/logout')
async def logout(request: Request):
    response = templates.TemplateResponse(request.url_for('index'), {'request': request})
    response.delete_cookie(key='access_token')
    return response
