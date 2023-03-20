from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import Test, Question, Answer
from db import database
from .auth import get_current_user


templates = Jinja2Templates(directory='templates')

router = APIRouter()


@router.get('/{topic_id}', response_class=HTMLResponse)
async def view_test(request: Request, topic_id: int, db: Session = Depends(database.get_session)):
    tests = db.query(Test).filter(Test.topic_id == topic_id).all()
    user = await get_current_user(request)
    return templates.TemplateResponse('test/index.html', {'request': request,
                                                             'title': 'Тести',
                                                             'tests': tests,
                                                             'user': user,
                                                             'topic_id': topic_id})


@router.get('/{topic_id}/add', response_class=HTMLResponse)
async def view_test_add(request: Request, topic_id: int):
    user = await get_current_user(request)
    return templates.TemplateResponse('test/add_test.html', {'request': request,
                                                            'title': 'Додати тему',
                                                            'user': user})
    
    
@router.get('/{topic_id}/edit/{test_id}', response_class=HTMLResponse)
async def view_test_edit(request: Request, topic_id: int, test_id: int, db: Session = Depends(database.get_session)):
    test = db.query(Test).filter(Test.id == test_id).first()
    user = await get_current_user(request)
    if test:
        return templates.TemplateResponse('test/edit_test.html', {'request': request,
                                                                'title': 'Тест тему',
                                                                'test': test,
                                                                'user': user})
    # TODO: edit
    return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)


@router.get('/{topic_id}/delete/{test_id}', response_class=HTMLResponse)
async def delete_test(request: Request, topic_id: int, test_id: int, db: Session = Depends(database.get_session)):
    db.query(Test).filter(Test.id == test_id).delete()
    return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)


@router.post('/{topic_id}/add', response_class=HTMLResponse)
async def add_test(request: Request, topic_id: int, db: Session = Depends(database.get_session)):
    form = await request.form()
    process_form_data(db, form, topic_id)
    
    return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)


@router.post('/{topic_id}/edit/{test_id}', response_class=HTMLResponse)
async def edit_test(request: Request, topic_id: int, test_id: int, name: str = Form(), db: Session = Depends(database.get_session)):
    test = db.query(Test).filter(Test.id == test_id).first()
    test.name = name
    # TODO: edit
    return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)


# Функція для розбору даних форми та запису їх в базу даних
async def process_form_data(db: Session, form_data: dict, topic_id: int):
    # Отримуємо дані з форми
    test_name = form_data.get('test_name')
    test_description = form_data.get('test_description')
    test_time = form_data.get('test_time')
    test_random = form_data.get('test_random')

    # Створюємо тест
    test = Test(name=test_name, description=test_description, time_to_complete=test_time, is_random=bool(test_random), topic_id=topic_id)
    db.add(test)
    db.commit()

    # Створюємо питання та відповіді
    for key, value in form_data.items():
        if key.startswith('question_'):
            question_text = value
            question = Question(text=question_text, test_id=test.id)
            db.add(question)
            db.commit()

            # Отримуємо всі відповіді для цього питання
            answers = []
            for subkey, subvalue in form_data.items():
                if subkey.startswith(f'answer_{key.split("_")[1]}_'):
                    answers.append((subkey, subvalue))

            # Створюємо відповіді
            for answer_key, answer_text in answers:
                is_correct_key = f'is_correct_{answer_key.split("_")[1]}_{answer_key.split("_")[2]}'
                is_correct = True if form_data.get(is_correct_key) else False
                answer = Answer(text=answer_text, is_correct=is_correct, question_id=question.id)
                db.add(answer)
                db.commit()
