import os
import uuid
import re
from datetime import datetime, timedelta
from typing import Optional, Type

from fastapi import Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import User
from .base_router import BaseRouter

import models
import utils
from db import database
from secrets import compare_digest


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')


class AuthRouter(BaseRouter):
    bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
    SECRET_KEY = "14pPK2rdJWVKfaqQvRn1DZu508KunWImLzP04Bxy5A7a9EEnnFo1ItGZlDJI"
    ALGORITHM = "HS256"

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_password_hash(password: str) -> str:
        return AuthRouter.bcrypt_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return AuthRouter.bcrypt_context.verify(plain_password, hashed_password)

    """ Authenticate user """

    def authenticate_user(self, email: str, password: str, db: Session) -> Type[User] | bool:
        user = db.query(models.User) \
            .filter(models.User.email == email) \
            .first()
        if not user or not self.verify_password(password, user.hashed_password):
            return False

        return user

    """ Generate user token """

    def create_access_token(self, email: str, user_id: str, role: str,
                            expires_delta: Optional[timedelta] = None):
        encode = {'sub': email, 'id': user_id, 'role': role}
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        encode.update({'exp': expire})
        return jwt.encode(encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    """ Get user by token """

    @staticmethod
    async def get_current_user(request: Request) -> None | dict:
        try:
            token = request.cookies.get('access_token')
            if token is None:
                return None
            payload = jwt.decode(token=token, key=AuthRouter.SECRET_KEY, algorithms=[AuthRouter.ALGORITHM])
            email: str = payload.get('sub')
            user_id: str = payload.get('id')
            role: str = payload.get('role')
            if email is None or user_id is None:
                AuthRouter.logout(request)
                return None

            return {'email': email, 'id': user_id, 'role': role}
        except JWTError:
            return None

    def init_get_function(self):

        """ View login form """

        @self.router.get('/login', response_class=HTMLResponse)
        async def view_login(request: Request):
            if await self.get_current_user(request):
                return RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)
            return self.templates.TemplateResponse('auth/login.html', {'request': request,
                                                                       'title': 'Вхід'})

        """ View register form """

        @self.router.get('/register', response_class=HTMLResponse)
        async def view_register(request: Request):
            if await self.get_current_user(request):
                return RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)
            return self.templates.TemplateResponse('auth/register.html', {'request': request,
                                                                          'title': 'Реєстрація'})

        """ Logout user """

        @self.router.get('/logout')
        async def logout(request: Request):
            return AuthRouter.logout(request)

    @staticmethod
    def logout(request: Request):
        response = AuthRouter.templates.TemplateResponse('home.html', {'request': request})
        response.delete_cookie(key='access_token')
        return response

    def init_post_function(self):

        """ Login and create user token """

        @self.router.post('/login', response_class=HTMLResponse)
        async def login(request: Request, db: Session = Depends(database.get_session)):
            try:
                form = LoginForm(request)
                await form.create_oauth_form()
                response = RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)

                validate_user_cookie = await self.login_for_access_token(response=response, form_data=form, db=db)

                if not validate_user_cookie:
                    msg = "Не вірні данні користувача"
                    return self.templates.TemplateResponse('auth/login.html', {'request': request,
                                                                               'title': 'Вхід',
                                                                               'msg': msg})
                return response
            except HTTPException:
                msg = "Невідома ошибка"
                return self.templates.TemplateResponse('auth/login.html', {'request': request,
                                                                           'title': 'Вхід',
                                                                           'msg': msg})

        """ Register user and add to database """

        @self.router.post('/register', response_class=HTMLResponse)
        async def register(request: Request, email: str = Form(), password: str = Form(),
                           password2: str = Form(), firstname: str = Form(),
                           lastname: str = Form(), img: str = Form(),
                           surname: Optional[str] = Form(None),
                           db: Session = Depends(database.get_session)):
            validation1 = db.query(models.User).filter(models.User.email == email).first()

            if validation1 is not None:
                msg = "Така пошта вже існує"
                return self.templates.TemplateResponse('auth/register.html', {'request': request,
                                                                              'title': 'Реєстрація',
                                                                              'msg': msg})

            if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{6,}$', password):
                msg = "Пароль відповідає всім вимогам"
                return self.templates.TemplateResponse('auth/register.html', {'request': request,
                                                                              'title': 'Реєстрація',
                                                                              'msg': msg})

            if not compare_digest(password, password2):
                msg = "Паролі не співпадають"
                return self.templates.TemplateResponse('auth/register.html', {'request': request,
                                                                              'title': 'Реєстрація',
                                                                              'msg': msg})

            if img == "null":
                msg = "Будь ласка зробіть фото"
                return self.templates.TemplateResponse('auth/register.html', {'request': request,
                                                                              'title': 'Реєстрація',
                                                                              'msg': msg})

            user_id = uuid.uuid4()

            file_path = f'static/users/images/{user_id}.png'

            utils.save_image_base64(img.split(',')[1], file_path)

            if utils.get_face_count(file_path) <= 0:
                msg = "На фото невидно лиця"
                os.remove(file_path)
                return self.templates.TemplateResponse('auth/register.html', {'request': request,
                                                                              'title': 'Реєстрація',
                                                                              'msg': msg})

            user = models.User(user_id=str(user_id), email=email, password=self.get_password_hash(password),
                               first_name=firstname, last_name=lastname, surname=surname,
                               path_to_image=file_path, is_active=True, role=1)
            db.add(user)
            return RedirectResponse(request.url_for('view_login'), status_code=status.HTTP_302_FOUND)

    """ Authenticate user and add token to cookie """

    async def login_for_access_token(self, response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                     db: Session = Depends(database.get_session)) -> bool:
        user = self.authenticate_user(form_data.username, form_data.password, db)
        if not user:
            return False
        role = db.query(models.Role).filter(models.Role.id == user.role_id).first().name
        token = self.create_access_token(email=user.email,
                                         user_id=user.user_id,
                                         role=role,
                                         expires_delta=timedelta(minutes=120))

        response.set_cookie(key='access_token', value=token, httponly=True)

        return True


auth = AuthRouter()
router = auth.get_router()
