import sys
sys.path.append("..")

from .auth import router, AuthRouter
from .subject import router
from .topic import router
from .test import router
from .user import router
