from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
import abc


class BaseRouter(abc.ABC):
    
    def __init__(self):
        self.templates = Jinja2Templates(directory='templates')
        self.router = APIRouter()
        self.init_get_function()
        self.init_post_function()
    
    @abc.abstractmethod
    def init_get_function(self):
        pass
    
    @abc.abstractmethod
    def init_post_function(self):
        pass
    
    def get_router(self) -> APIRouter:
        return self.router
    