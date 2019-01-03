"""
login extension for user management
"""

from flask_login import LoginManager
from .conf import conf
from flask import request
from .exceptions import PermissionDenied


def login_redirect():
    if request.path.startswith("/api/"):
        raise PermissionDenied(message="Please log in first")
    else:
        from .views import login
        return login()

login_manager = LoginManager()
# login_manager.login_view = 'userview.login'
login_manager.unauthorized_handler(login_redirect)
login_manager.session_protection = conf['LOGIN_SESSION_PROTECTION']
