from flask import Flask
from .models import db
from celery import Celery
from .helper import register_blueprints
from .utils import *  # used for filters of jinja
from .errorhandler import *  # used for errorhandlers of the app
from .exceptions import *
from .loginmanager import login_manager
from .conf import conf
import os
from sqlalchemy import exc  # exception base for sqlalchemy
import logging
from .logs import log_init_app


def create_app(blueprints=True, dbcreate=conf.get("DB_CREATE", False), testconf=None):
    app = Flask(__name__)
    app.config.update(conf)
    if testconf:
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
    login_manager.init_app(app)
    if app.config.get("JINJA_FILTERS", None):
        for filter in app.config["JINJA_FILTERS"]:
            app.jinja_env.filters[filter] = globals()[filter]
    for item in globals():
        if item.startswith("on_"):
            app.logger.info("register %s as error handler" % item)
            try:
                app.register_error_handler(globals()[item[3:]], globals()[item])
            except:
                app.register_error_handler(int(item[3:]), globals()[item])
    # app.register_error_handler(404, on_404)
    # app.register_error_handler(InvalidInput, on_invalidinput)
    print("app.debug: %s" % app.debug)

    if blueprints is True:
        register_blueprints(app, "app", os.path.dirname(os.path.abspath(__file__)))
        log_init_app(app)

    return app


def create_celery_app(app=None):
    app = app or create_app(blueprints=False, dbcreate=False)
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
