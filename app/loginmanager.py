"""
login extension for user management
"""

from flask_login import LoginManager, current_user
from functools import wraps
from flask import request, abort

from .conf import conf
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


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user:
            abort(404)
        if not current_user.is_admin():
            abort(404)
        return func(*args, **kwargs)

    return decorated_view
