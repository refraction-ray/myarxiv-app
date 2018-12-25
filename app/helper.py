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


def get_config(overide=None):
    dirpath = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dirpath, "config.yaml"), 'r') as conffile:
        conf = load(conffile, Loader=Loader)
    if overide:
        with open(os.path.join(dirpath, overide), "r") as conffile:
            confo = load(conffile, Loader=Loader)
        conf.update(confo)
    return conf


def register_blueprints(app, package_name, package_path):
    """Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.
    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """
    rv = []
    # print(package_path)
    for _, name, _ in pkgutil.iter_modules([package_path]):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
                print(item)
            rv.append(item)
    return rv
