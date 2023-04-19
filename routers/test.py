from fastapi import Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from datetime import timedelta
from typing import Dict

from models import Test, Question, Answer, CompletedTest
from db import database
from .auth import AuthRouter
from .base_router import BaseRouter

import utils
import random


class TestRouter(BaseRouter):

    def __init__(self):
        super().__init__()

    def init_get_function(self):
        @self.router.get('/compleat/{compleat_id}', response_class=HTMLResponse)
        async def view_compleat(request: Request, compleat_id: int, db: Session = Depends(database.get_session)):
            comp = db.query(CompletedTest).filter(CompletedTest.id == compleat_id).first()
            user = await AuthRouter.get_current_user(request)
            score = utils.get_score(comp.score)
            return self.templates.TemplateResponse('test/compleat_test.html',
                                                   {'request': request, 'score': score, 'user': user,
                                                    'title': 'Результат тесту'})

        @self.router.get('/tester/{test_id}', response_class=HTMLResponse)
        async def view_tester(request: Request, test_id: int, db: Session = Depends(database.get_session)):
            if not utils.check_test_token(request, test_id):
                return RedirectResponse(request.url_for('index'), status_code=status.HTTP_302_FOUND)
            user = await AuthRouter.get_current_user(request)
            test_object = db.query(Test).filter(Test.id == test_id).first()

            answers = []

            questions = db.query(Question).filter(Question.test_id == test_id).all()

            for i in questions:
                temp = db.query(Answer).filter(Answer.question_id == i.id).all()
                answers.extend(temp)

            if test_object.is_random:
                random.shuffle(questions)
                random.shuffle(answers)
            return self.templates.TemplateResponse('test/pass_the_test.html', {'request': request,
                                                                               'title': 'Проходження тесту',
                                                                               'questions': questions,
                                                                               'answers': answers,
                                                                               'timer': test_object.time_to_complete,
                                                                               'user': user})

        @self.router.get('/check/{test_id}', response_class=HTMLResponse)
        async def view_check_person(request: Request, test_id: int, db: Session = Depends(database.get_session)):
            user = await AuthRouter.get_current_user(request)
            test_object = db.query(Test).filter(Test.id == test_id).first()
            if user is None:
                return RedirectResponse(request.url_for('view_test', topic_id=test_object.topic_id),
                                        status_code=status.HTTP_302_FOUND)
            return self.templates.TemplateResponse('test/check_user_face.html', {'request': request,
                                                                                 'title': 'Перевірка користувача',
                                                                                 'user': user})

        @self.router.get('/{topic_id}', response_class=HTMLResponse)
        async def view_test(request: Request, topic_id: int, db: Session = Depends(database.get_session)):
            tests = db.query(Test).filter(Test.topic_id == topic_id).all()
            user = await AuthRouter.get_current_user(request)

            return self.templates.TemplateResponse('test/index.html', {'request': request,
                                                                       'title': 'Тести',
                                                                       'tests': tests,
                                                                       'user': user,
                                                                       'topic_id': topic_id})

        @self.router.get('/{topic_id}/add', response_class=HTMLResponse)
        async def view_test_add(request: Request):
            user = await AuthRouter.get_current_user(request)
            return self.templates.TemplateResponse('test/add_test.html', {'request': request,
                                                                          'title': 'Додати тест',
                                                                          'user': user})

        @self.router.get('/{topic_id}/edit/{test_id}', response_class=HTMLResponse)
        async def view_test_edit(request: Request, topic_id: int, test_id: int,
                                 db: Session = Depends(database.get_session)):
            test_object = db.query(Test).filter(Test.id == test_id).first()
            user = await AuthRouter.get_current_user(request)
            if test_object:
                questions = await self.get_question(db, test_object.id)
                return self.templates.TemplateResponse('test/edit_test.html', {'request': request,
                                                                               'title': 'Змінити тест',
                                                                               'test': test_object,
                                                                               'questions': questions,
                                                                               'user': user})
            return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)

        @self.router.get('/{topic_id}/delete/{test_id}', response_class=HTMLResponse)
        async def delete_test(request: Request, topic_id: int, test_id: int,
                              db: Session = Depends(database.get_session)):
            questions = db.query(Question).filter(Question.test_id == test_id).all()
            for q in questions:
                db.query(Answer).filter(Answer.question_id == q.id).delete()
            db.query(Question).filter(Question.test_id == test_id).delete()
            db.query(Test).filter(Test.id == test_id).delete()
            return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)

    def init_post_function(self):
        @self.router.post('/{topic_id}/add', response_class=HTMLResponse)
        async def add_test(request: Request, topic_id: int, db: Session = Depends(database.get_session)):
            form = await request.form()

            test_name = form.get('test_name')
            test_description = form.get('test_description')
            test_time = form.get('test_time')
            test_random = form.get('test_random')

            # Створюємо тест
            test_object = Test(name=test_name, description=test_description, time_to_complete=test_time,
                               is_random=bool(test_random), topic_id=topic_id)
            db.add(test_object)
            db.commit()
            await self.process_form_data(db, form, test_object.id)

            return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)

        @self.router.post('/check/{test_id}', response_class=HTMLResponse)
        async def check_person(request: Request, test_id: int, img: str = Form(),
                               db: Session = Depends(database.get_session)):
            user = await AuthRouter.get_current_user(request)

            file_path_temp = f'static/users/check_images/{user["id"]}.png'
            file_path_user = f'static/users/images/{user["id"]}.png'
            utils.save_image_base64(img.split(',')[1], file_path_temp)

            if utils.check_face(file_path_user, file_path_temp):
                test_object = db.query(Test).filter(Test.id == test_id).first()
                token = utils.gen_test_token(test_object.id, timedelta(minutes=test_object.time_to_complete))
                response = RedirectResponse(request.url_for('view_tester', test_id=test_object.id),
                                            status_code=status.HTTP_302_FOUND)
                response.set_cookie('test_token', token)
                return response

            return self.templates.TemplateResponse('test/check_user_face.html', {'request': request,
                                                                                 'title': 'Перевірка користувача',
                                                                                 'msg': "Користувача не підтверджено! "
                                                                                        "Попробуйте зробити фото знову "
                                                                                        "або оновити його у профілі."})

        @self.router.post('/{topic_id}/edit/{test_id}', response_class=HTMLResponse)
        async def edit_test(request: Request, topic_id: int, test_id: int, db: Session = Depends(database.get_session)):
            test_object = db.query(Test).filter(Test.id == test_id).first()
            form = await request.form()

            test_object.name = form.get('test_name')
            test_object.description = form.get('test_description')
            test_object.time_to_complete = form.get('test_time')
            if form.get('test_random') is not None:
                test_object.is_random = form.get('test_random')

            questions = db.query(Question).filter(Question.test_id == test_id).all()
            for q in questions:
                db.query(Answer).filter(Answer.question_id == q.id).delete()
            db.query(Question).filter(Question.test_id == test_id).delete()

            db.commit()

            await self.process_form_data(db, form, test_object.id)

            return RedirectResponse(request.url_for('view_test', topic_id=topic_id), status_code=status.HTTP_302_FOUND)

        @self.router.post('/tester/{test_id}', response_class=HTMLResponse)
        async def get_tester(request: Request, test_id: int, db: Session = Depends(database.get_session)):
            form = await request.form()
            score = await self.calculate_score(db, test_id, form)
            user = await AuthRouter.get_current_user(request)
            db.add(CompletedTest(form.get('user_id', ''), test_id, score))
            db.commit()

            comp_id = db.query(CompletedTest).filter(CompletedTest.user_id is user['id'],
                                                     CompletedTest.test_id == test_id,
                                                     CompletedTest.score == score).first().id

            response = RedirectResponse(request.url_for('view_compleat', compleat_id=comp_id),
                                        status_code=status.HTTP_302_FOUND)
            response.delete_cookie('test_token')
            return response

    # Функція для розбору даних форми та запису їх в базу даних

    @staticmethod
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

    @staticmethod
    async def process_form_data(db: Session, form_data: dict, test_id: int):
        # Створюємо питання та відповіді
        for key, value in form_data.items():
            if key.startswith('question_'):
                question_text = value
                question = Question(text=question_text, test_id=test_id)
                db.add(question)
                db.commit()

                # Отримуємо всі відповіді для цього питання
                answers = []
                for subkey, sub_value in form_data.items():
                    if subkey.startswith(f'answer_{key.split("_")[1]}_'):
                        answers.append((subkey, sub_value))

                # Створюємо відповіді
                for answer_key, answer_text in answers:
                    is_correct_key = f'is_correct_{answer_key.split("_")[1]}_{answer_key.split("_")[2]}'
                    is_correct = True if form_data.get(is_correct_key) else False
                    answer = Answer(text=answer_text, is_correct=is_correct, question_id=question.id)
                    db.add(answer)
                    db.commit()

    @staticmethod
    async def get_question(db: Session, test_id: int):
        questions = db.query(Question).filter(Question.test_id == test_id).all()
        questions_dict = []
        for q in questions:
            answers = db.query(Answer).filter(Answer.question_id == q.id).all()
            answers_dict = [{"text": a.text, "is_correct": a.is_correct} for a in answers]
            q_dict = {"text": q.text, "answers": answers_dict}
            questions_dict.append(q_dict)

        return questions_dict


test = TestRouter()
router = test.get_router()
