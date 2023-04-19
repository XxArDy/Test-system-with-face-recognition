from fastapi import Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import Topic
from db import database
from .auth import AuthRouter
from .base_router import BaseRouter


class TopicRouter(BaseRouter):

    def __init__(self):
        super().__init__()

    def init_get_function(self):
        @self.router.get('/{subject_id}', response_class=HTMLResponse)
        async def view_topic(request: Request, subject_id: int, db: Session = Depends(database.get_session)):
            topics = db.query(Topic).filter(Topic.subject_id == subject_id).all()
            user = await AuthRouter.get_current_user(request)
            return self.templates.TemplateResponse('topic/index.html', {'request': request,
                                                                        'title': 'Теми',
                                                                        'topics': topics,
                                                                        'user': user,
                                                                        'subject_id': subject_id})

        @self.router.get('/{subject_id}/add', response_class=HTMLResponse)
        async def view_topic_add(request: Request):
            user = await AuthRouter.get_current_user(request)
            return self.templates.TemplateResponse('topic/add_topic.html', {'request': request,
                                                                            'title': 'Додати тему',
                                                                            'user': user})

        @self.router.get('/{subject_id}/edit/{topic_id}', response_class=HTMLResponse)
        async def view_topic_edit(request: Request, subject_id: int, topic_id: int,
                                  db: Session = Depends(database.get_session)):
            topic_object = db.query(Topic).filter(Topic.id == topic_id).first()
            user = await AuthRouter.get_current_user(request)
            if topic_object:
                return self.templates.TemplateResponse('topic/edit_topic.html', {'request': request,
                                                                                 'title': 'Змінити тему',
                                                                                 'topic': topic_object,
                                                                                 'user': user})
            return RedirectResponse(request.url_for('view_topic', subject_id=subject_id),
                                    status_code=status.HTTP_302_FOUND)

        @self.router.get('/{subject_id}/delete/{topic_id}', response_class=HTMLResponse)
        async def delete_topic(request: Request, subject_id: int, topic_id: int,
                               db: Session = Depends(database.get_session)):
            db.query(Topic).filter(Topic.id == topic_id).delete()
            return RedirectResponse(request.url_for('view_topic', subject_id=subject_id),
                                    status_code=status.HTTP_302_FOUND)

    def init_post_function(self):
        @self.router.post('/{subject_id}/add', response_class=HTMLResponse)
        async def add_topic(request: Request, subject_id: int, name: str = Form(),
                            db: Session = Depends(database.get_session)):
            topic_object = Topic(name=name, subject_id=subject_id)
            db.add(topic_object)
            return RedirectResponse(request.url_for('view_topic', subject_id=subject_id),
                                    status_code=status.HTTP_302_FOUND)

        @self.router.post('/{subject_id}/edit/{topic_id}', response_class=HTMLResponse)
        async def edit_topic(request: Request, subject_id: int, topic_id: int, name: str = Form(),
                             db: Session = Depends(database.get_session)):
            topic_object = db.query(Topic).filter(Topic.id == topic_id).first()
            topic_object.name = name
            return RedirectResponse(request.url_for('view_topic', subject_id=subject_id),
                                    status_code=status.HTTP_302_FOUND)


topic = TopicRouter()
router = topic.get_router()
