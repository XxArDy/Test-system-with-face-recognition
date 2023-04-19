from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
import abc


""" Base class for all routers"""


class BaseRouter(abc.ABC):
    templates = Jinja2Templates(directory='templates')

    def __init__(self):
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
    