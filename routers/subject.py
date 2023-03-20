from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import Subject
from db import database
from .auth import get_current_user


templates = Jinja2Templates(directory='templates')

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def view_subject(request: Request, db: Session = Depends(database.get_session)):
    subjects = db.query(Subject).all()
    user = await get_current_user(request)
    return templates.TemplateResponse('subject/index.html', {'request': request,
                                                             'title': 'Предмети',
                                                             'subjects': subjects,
                                                             'user': user})
    

@router.get('/add', response_class=HTMLResponse)
async def view_subject_add(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse('subject/add_subject.html', {'request': request,
                                                                   'title': 'Додати предмет',
                                                                   'user': user})
    
    
@router.get('/edit/{subject_id}', response_class=HTMLResponse)
async def view_subject_edit(request: Request, subject_id: int, db: Session = Depends(database.get_session)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    user = await get_current_user(request)
    if subject:
        return templates.TemplateResponse('subject/edit_subject.html', {'request': request,
                                                                'title': 'Змінити предмет',
                                                                'subject': subject,
                                                                'user': user})
    return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)


@router.get('/delete/{subject_id}', response_class=HTMLResponse)
async def delete_subject(request: Request, subject_id: int, db: Session = Depends(database.get_session)):
    db.query(Subject).filter(Subject.id == subject_id).delete()
    return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)


@router.post('/add', response_class=HTMLResponse)
async def add_subject(request: Request, name: str = Form(), db: Session = Depends(database.get_session)):
    subject = Subject(name)
    db.add(subject)
    return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)


@router.post('/edit/{subject_id}', response_class=HTMLResponse)
async def edit_subject(request: Request, subject_id: int, name: str = Form(), db: Session = Depends(database.get_session)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    subject.name = name
    return RedirectResponse(request.url_for('view_subject'), status_code=status.HTTP_302_FOUND)
