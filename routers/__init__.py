import sys
sys.path.append("..")

from .auth import router, get_current_user
from .subject import router
from .topic import router
from .test import router
