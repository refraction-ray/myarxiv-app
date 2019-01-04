from app.tasks import celery
from .conftest import testconf

def test_config(app):
    assert app.config["TESTING"] is True


def test_logger(app):
    logger = app.logger
    assert len(logger.handlers) == 1
    assert logger.name == "flask.app"


def test_celery_config(app):
    assert celery.conf.broker_url == testconf['BROKER_URL']
    assert celery.conf.result_backend == testconf['CELERY_RESULT_BACKEND']
