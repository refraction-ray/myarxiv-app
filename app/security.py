"""
security token related stuff
"""

from itsdangerous import URLSafeTimedSerializer, BadData
from .conf import conf
from functools import wraps
from flask import request, current_app
from .exceptions import PermissionDenied
from flask_login import current_user

ts = URLSafeTimedSerializer(conf["SECRET_KEY"])


def token_checked(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method != "POST":
            return f(*args, **kwargs)
        current_app.logger.info("the csrf token is checked for safety")
        token = request.form.get("ctoken", None)
        if not token:
            try:
                token = request.json.get("ctoken", "")
            except AttributeError:
                token = ""
        try:
            uid = ts.loads(token, max_age=conf['CTOKEN_EXPIRE_SECONDS'])
        except (TypeError, BadData) as e:
            raise PermissionDenied(message="The token was expired, please reload the page.")
        if uid != current_user.id:
            raise PermissionDenied(message="The token was expired, please reload the page.")
        return f(*args, **kwargs)

    return decorated_function
