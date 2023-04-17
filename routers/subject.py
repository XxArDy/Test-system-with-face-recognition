from fastapi import Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import Subject
from db import database
from .auth import AuthRouter

from .base_router import BaseRouter


class SubjectRouter(BaseRouter):
    
    def __init__(self):
        super().__init__()
        
    def init_get_function(self):
        @self.router.get('/', response_class=HTMLResponse)
        async def view_subject(request: Request, db: Session = Depends(database.get_session)):
            subjects = db.query(Subject).all()
            user = await AuthRouter.get_current_user(request)
            return self.templates.TemplateResponse('subject/index.html', {'request': request,
                                                                    'title': 'Предмети',
                                                                    'subjects': subjects,
                                                                    'user': user})
            

        @self.router.get('/add', response_class=HTMLResponse)
        async def view_subject_add(request: Request):
            user = await AuthRouter.get_current_user(request)
            return self.templates.TemplateResponse('subject/add_subject.html', {'request': request,
                                                                        'title': 'Додати предмет',
                                                                        'user': user})
            
            
        @self.router.get('/edit/{subject_id}', response_class=HTMLResponse)
        async def view_subject_edit(request: Request, subject_id: int, db: Session = Depends(database.get_session)):
            subject = db.query(Subject).filter(Subject.id == subject_id).first()
            user = await AuthRouter.get_current_user(request)
            if subject:
                return self.templates.TemplateResponse('subject/edit_subject.html', {'request': request,
                                                                        'title': 'Змінити предмет',
                                                                        'subject': subject,
                                                                        'user': user})
            return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)


        @self.router.get('/delete/{subject_id}', response_class=HTMLResponse)
        async def delete_subject(request: Request, subject_id: int, db: Session = Depends(database.get_session)):
            db.query(Subject).filter(Subject.id == subject_id).delete()
            return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)

    def init_post_function(self):
        @self.router.post('/add', response_class=HTMLResponse)
        async def add_subject(request: Request, name: str = Form(), db: Session = Depends(database.get_session)):
            subject = Subject(name)
            db.add(subject)
            return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)


        @self.router.post('/edit/{subject_id}', response_class=HTMLResponse)
        async def edit_subject(request: Request, subject_id: int, name: str = Form(), db: Session = Depends(database.get_session)):
            subject = db.query(Subject).filter(Subject.id == subject_id).first()
            subject.name = name
            return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)

subject = SubjectRouter()

router = subject.get_router()
