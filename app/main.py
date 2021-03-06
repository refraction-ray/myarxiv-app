"""
main module for create_app and factory pattern
"""

from flask import Flask
import os
from sqlalchemy import exc  # exception base for sqlalchemy
from celery import Celery

from .models import db
from .helper import register_blueprints, register_errorhandlers, register_jinja_filters
from .utils import *  # used for filters of jinja
from .errorhandler import *  # used for errorhandlers of the app
from .exceptions import *
from .loginmanager import login_manager
from .conf import conf
from .logs import log_init_app
from .manage import admin


def create_app(blueprints=True, dbcreate=conf.get("DB_CREATE", False), testconf=None):
    print("------------")
    print("entering create_app()")
    app = Flask(__name__)
    app.config.update(conf)
    if testconf:
        print("update config based on testconf")
        app.config.update(testconf)
    db.init_app(app)
    if dbcreate is True and app.config.get("DB_CREATE", False):
        with app.app_context():
            try:
                db.create_all()  ## if it is directly started by gunicorn, there might be several table insert at the same time
                ## but the error is ok if gunicorn is watched by supervisord
            except exc.OperationalError:
                print("Maybe something went wrong on creating tables in mysql")
    app.secret_key = conf['SECRET_KEY'].encode('utf8')
    # app.register_error_handler(404, on_404)
    # app.register_error_handler(InvalidInput, on_invalidinput)
    print("app.debug: %s" % app.debug)

    if blueprints is True:
        register_blueprints(app, "app", os.path.dirname(os.path.abspath(__file__)))
        log_init_app(app)
        admin.init_app(app)
        login_manager.init_app(app)
        register_errorhandlers(app, globals())
        register_jinja_filters(app, globals())

    print("finish the app factory")
    print("------------")
    return app


def create_celery_app(app=None, testconf=None):
    app = app or create_app(blueprints=False, dbcreate=False, testconf=testconf)
    celery = Celery(__name__, broker=app.config['BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
