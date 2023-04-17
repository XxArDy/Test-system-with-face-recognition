from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import database
from routers import *
from starlette.staticfiles import StaticFiles


class MyApp:
    def __init__(self):
        self.app = FastAPI()
        self.templates = Jinja2Templates(directory='templates')
        database.init_db()
        self.app.mount('/static', StaticFiles(directory='static'), name='static')
        self.include_routers()
        self.include_request()

    def include_routers(self):
        self.app.include_router(auth.router, prefix='/auth', tags=['auth'])
        self.app.include_router(subject.router, prefix='/subjects', tags=['subject'])
        self.app.include_router(topic.router, prefix='/topics', tags=['topic'])
        self.app.include_router(test.router, prefix='/test', tags=['test'])
        self.app.include_router(user.router, prefix='/user', tags=['user'])

    def include_request(self):
        @self.app.get('/', response_class=HTMLResponse)
        async def index(request: Request):
            user = await AuthRouter.get_current_user(request)
            return self.templates.TemplateResponse('home.html', {'request': request,
                                                                'title': 'Home',
                                                                'user': user})

    def start(self):
        return self.app;


myApp = MyApp()
app = myApp.start()
