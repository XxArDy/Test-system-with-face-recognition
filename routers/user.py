import os

from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette import status

from db import database
from .auth import AuthRouter
from models import User, CompletedTest, Test
from utils import get_face_count, save_image_base64
from .base_router import BaseRouter


class UserRouter(BaseRouter):

    def __init__(self):
        super().__init__()

    def init_get_function(self):
        @self.router.get('/', response_class=HTMLResponse)
        async def view_user_profile(request: Request, db: Session = Depends(database.get_session)):
            user_dict = await AuthRouter.get_current_user(request)

            if user_dict is None:
                return RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)

            user_dict = db.query(User).filter(User.email == user_dict["email"]).first()
            test = db.query(Test).all()
            completed_test = db.query(CompletedTest).filter(CompletedTest.user_id == user_dict.user_id).all()

            return self.templates.TemplateResponse('user/index.html',
                                                   {'request': request, 'tests': completed_test, "all_test": test,
                                                    'user': user_dict, 'title': 'Твій профіль',
                                                    'user_photo': user_dict.path_to_image.replace('static', '')})

    def init_post_function(self):
        @self.router.post('/change/password')
        async def change_password(request: Request, current_password: str = Form(),
                                  new_password: str = Form(), db: Session = Depends(database.get_session)):
            user_dict = await AuthRouter.get_current_user(request)
            if user_dict is None:
                return RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)
            user_dict = db.query(User).filter(User.email == user_dict["email"]).first()
            if not AuthRouter.verify_password(current_password, user_dict.hashed_password):
                return {"result": False}

            user_dict.hashed_password = AuthRouter.get_password_hash(new_password)
            return {"result": True}

        @self.router.post('/change/image')
        async def change_image(request: Request, img: str = Form(), db: Session = Depends(database.get_session)):
            user_dict = await AuthRouter.get_current_user(request)
            if user_dict is None:
                return RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)
            user_dict = db.query(User).filter(User.email == user_dict["email"]).first()
            file_path_check = f'static/users/check_images/{user_dict.user_id}.png'
            save_image_base64(img.split(',')[1], file_path_check)

            if get_face_count(file_path_check) <= 0:
                os.remove(file_path_check)
                return {"result": False}

            os.remove(file_path_check)
            file_path = f'static/users/images/{user_dict.user_id}.png'
            save_image_base64(img.split(',')[1], file_path)

            return {"result": True}


user = UserRouter()
router = user.get_router()
