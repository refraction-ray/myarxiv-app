"""
Exception class of the app
As well as common messages
"""
from .conf import maildict, conf


class AppError(Exception):  # base exception of the web app
    pass


class AppAPIError(AppError):  # abstract error, directly use not recommended
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class InvalidInput(AppAPIError):
    status_code = 422


class PermissionDenied(AppAPIError):
    status_code = 403


appmessage = {
    "mail_check": """
    If you cannot find the mail, you should check junk mails.\n
    Please make sure the mail address is our official address %s.
    """ % maildict['sender'],

    "mail_start": """
    This is the mail from %s.\n
    """ % conf['MAIL_ABS_PATH']
}
