from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from datetime import timedelta
from typing import Dict

from models import Test, Question, Answer, CompletedTest
from db import database
from .auth import get_current_user

import utils


templates = Jinja2Templates(directory='templates')

router = APIRouter()


@router.get('/compleat/{compleat_id}', response_class=HTMLResponse)
async def view_compleat(request: Request, compleat_id: int, db: Session = Depends(database.get_session)):
    comp = db.query(CompletedTest).filter(CompletedTest.id == compleat_id).first()
    user = await get_current_user(request)
    score = utils.get_score(comp.score)
    return templates.TemplateResponse('test/compleat_test.html', {'request': request, 'score': score, 'user': user})
    

@router.get('/tester/{test_id}', response_class=HTMLResponse)
async def view_tester(request: Request, test_id: int, db: Session = Depends(database.get_session)):
    if not utils.check_test_token(request, test_id):
        return RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)
    user = await get_current_user(request)
    test = db.query(Test).filter(Test.id == test_id).first()
    
    answers = []
    
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    
    for i in questions:
        temp = db.query(Answer).filter(Answer.question_id == i.id).all()
        answers.extend(temp)
    return templates.TemplateResponse('test/pass_the_test.html', {'request': request,
                                                                    'title': 'Проходження тесту',
                                                                    'questions': questions,
                                                                    'answers': answers, 
                                                                    'timer': test.time_to_complete,
                                                                    'user': user})


@router.get('/check/{test_id}', response_class=HTMLResponse)
async def view_check_person(request: Request, test_id: int, db: Session = Depends(database.get_session)):
    user = await get_current_user(request)
    test = db.query(Test).filter(Test.id == test_id).first()
    if user is None:
        return RedirectResponse(request.url_for('view_test', topic_id=test.topic_id), status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('test/check_user_face.html', {'request': request,
                                                                    'title': 'Проверка користувача',
                                                                    'user': user})


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
                                                            'title': 'Додати тест',
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
    await process_form_data(db, form, topic_id)
    
    return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)


@router.post('/check/{test_id}', response_class=HTMLResponse)
async def check_person(request: Request, test_id: int, img: str = Form(), db: Session = Depends(database.get_session)):
    user = await get_current_user(request)
    
    file_path_temp = f'static/users/check_images/{user["id"]}.png'
    file_path_user = f'static/users/images/{user["id"]}.png'
    utils.save_image_base64(img.split(',')[1], file_path_temp)
    
    if utils.check_face(file_path_user, file_path_temp):
        test = db.query(Test).filter(Test.id == test_id).first()
        token = utils.gen_test_token(test.id, timedelta(minutes=test.time_to_complete))
        responce = RedirectResponse(request.url_for('view_tester', test_id=test.id), status_code=status.HTTP_302_FOUND)
        responce.set_cookie('test_token', token)
        return responce
    
    return templates.TemplateResponse('test/check_user_face.html', {'request': request,
                                                                    'title': 'Проверка користувача',
                                                                    'msg': "Користувача не підтверджено! Попробуйте зробити фото знову або оновити його у профілі."})


@router.post('/{topic_id}/edit/{test_id}', response_class=HTMLResponse)
async def edit_test(request: Request, topic_id: int, test_id: int, name: str = Form(), db: Session = Depends(database.get_session)):
    test = db.query(Test).filter(Test.id == test_id).first()
    test.name = name
    # TODO: edit
    return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)


@router.post('/tester/{test_id}', response_class=HTMLResponse)
async def get_tester(request: Request, test_id: int, db: Session = Depends(database.get_session)):
    form = await request.form()
    score = await calculate_score(db, test_id, form)
    user = await get_current_user(request)
    db.add(CompletedTest(form.get('user_id', ''), test_id, score))
    db.commit() 
    comp_id = db.query(CompletedTest).filter(CompletedTest.user_id == user['id'] 
                                            and CompletedTest.test_id == test_id 
                                            and CompletedTest.score == score).first().id
    responce = RedirectResponse(request.url_for('view_compleat', compleat_id=comp_id), status_code=status.HTTP_302_FOUND)
    responce.delete_cookie('test_token')
    return responce
    
    


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


async def calculate_score(db: Session, test_id: int, form: Dict[str, str]) -> float:
    score = 0
    questions = db.query(Question).filter(Question.test_id == test_id).all()

    for question in questions:
        answers = db.query(Answer).filter(Answer.question_id == question.id).all()
        correct_answers = sum([1 for a in answers if a.is_correct])
        correct_count = sum([1 for a in answers if form.get(f'is_correct_{question.id}_{a.id}', '')])
        if correct_count == correct_answers:
            score += 1

    return round(score / len(questions) * 100, 2)