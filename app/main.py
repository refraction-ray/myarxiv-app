from flask import Flask
from .models import db
from celery import Celery
from .helper import register_blueprints
from .utils import *   # used for filters of jinja
from .errorhandler import *  # used for errorhandlers of the app
from .exceptions import *
from .loginmanager import login_manager
from .conf import conf
from os import path



def create_app(blueprints=True):
    app = Flask(__name__)
    app.config.update(conf)
    db.init_app(app)
    app.secret_key = conf['SECRET_KEY'].encode('utf8')
    login_manager.init_app(app)
    if conf.get("JINJA_FILTERS", None):
        for filter in conf["JINJA_FILTERS"]:
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
    if blueprints is True:
        register_blueprints(app, "app", path.abspath("./app"))

    return app


def create_celery_app(app=None):
    app = app or create_app(blueprints=False)
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
