from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import engine, Base
from routers import *
from starlette.staticfiles import StaticFiles


app = FastAPI()

# Create database
Base.metadata.create_all(bind=engine)

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

app.include_router(auth.router,
                   prefix='/auth',
                   tags=['auth'])


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('home.html', {'request': request,
                                                    'title': 'Home'})
    