"""
some assistant functions to start the app
"""

import pkgutil
import importlib
import os
from flask import Blueprint
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def get_config(name=None, override=None, path=None):
    if not path:
        dirpath = os.path.dirname(os.path.abspath(__file__))
    else:
        dirpath = path
    if not name:
        name = "config.yaml"
    with open(os.path.join(dirpath, name), 'r') as conffile:
        conf = load(conffile, Loader=Loader)
    if override:
        try:
            with open(os.path.join(dirpath, override), "r") as conffile:
                confo = load(conffile, Loader=Loader)
            conf.update(confo)
        except FileNotFoundError:
            pass
    return conf


def register_blueprints(app, package_name, package_path):
    """Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.
    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """
    rv = []
    blist = ["views", "api"]
    for _, name, _ in pkgutil.iter_modules([package_path]):
        if name in blist:
            m = importlib.import_module('%s.%s' % (package_name, name))
            for item in dir(m):
                item = getattr(m, item)
                if isinstance(item, Blueprint):
                    app.register_blueprint(item)
                    print(item)
                rv.append(item)
    return rv


def register_errorhandlers(app, env):
    for item in env:
        if item.startswith("on_"):
            # app.logger.info("register %s as error handler" % item)
            try:
                app.register_error_handler(env[item[3:]], env[item])
            except:
                app.register_error_handler(int(item[3:]), env[item])


def register_jinja_filters(app, env):
    if app.config.get("JINJA_FILTERS", None):
        for filter in app.config["JINJA_FILTERS"]:
            app.jinja_env.filters[filter] = env[filter]
