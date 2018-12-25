"""
login extension for user management
"""

from flask_login import LoginManager
from .conf import conf

login_manager = LoginManager()
login_manager.login_view = 'userview.login'
login_manager.session_protection = conf['LOGIN_SESSION_PROTECTION']
