from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import Topic, Subject
from db import database
from .auth import get_current_user


templates = Jinja2Templates(directory='templates')

router = APIRouter()


@router.get('/{subject_id}', response_class=HTMLResponse)
async def view_topic(request: Request, subject_id: int, db: Session = Depends(database.get_session)):
    topics = db.query(Topic).filter(Topic.subject_id == subject_id).all()
    user = await get_current_user(request)
    return templates.TemplateResponse('topic/index.html', {'request': request,
                                                             'title': 'Теми',
                                                             'topics': topics,
                                                             'user': user,
                                                             'subject_id': subject_id})
    

@router.get('/{subject_id}/add', response_class=HTMLResponse)
async def view_topic_add(request: Request, subject_id: int):
    user = await get_current_user(request)
    return templates.TemplateResponse('topic/add_topic.html', {'request': request,
                                                                   'title': 'Додати тему',
                                                                   'user': user})
    
    
@router.get('/{subject_id}/edit/{topic_id}', response_class=HTMLResponse)
async def view_topic_edit(request: Request, subject_id: int, topic_id: int, db: Session = Depends(database.get_session)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    user = await get_current_user(request)
    if topic:
        return templates.TemplateResponse('topic/edit_topic.html', {'request': request,
                                                                'title': 'Змінити тему',
                                                                'topic': topic,
                                                                'user': user})
    return RedirectResponse(request.url_for('view_topic', subject_id=subject_id), status_code=status.HTTP_302_FOUND)


@router.get('/{subject_id}/delete/{topic_id}', response_class=HTMLResponse)
async def delete_topic(request: Request, subject_id: int, topic_id: int, db: Session = Depends(database.get_session)):
    db.query(Topic).filter(Topic.id == topic_id).delete()
    return RedirectResponse(request.url_for('view_topic', subject_id=subject_id), status_code=status.HTTP_302_FOUND)


@router.post('/{subject_id}/add', response_class=HTMLResponse)
async def add_topic(request: Request, subject_id: int, name: str = Form(), db: Session = Depends(database.get_session)):
    topic = Topic(name=name, subject_id=subject_id)
    db.add(topic)
    return RedirectResponse(request.url_for('view_topic', subject_id=subject_id), status_code=status.HTTP_302_FOUND)


@router.post('/{subject_id}/edit/{topic_id}', response_class=HTMLResponse)
async def edit_topic(request: Request, subject_id: int, topic_id: int, name: str = Form(), db: Session = Depends(database.get_session)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    topic.name = name
    return RedirectResponse(request.url_for('view_topic', subject_id=subject_id), status_code=status.HTTP_302_FOUND)
