import logging

def test_config(app):
    assert app.config["TESTING"] is True

def test_logger(app):
    logger = app.logger
    assert len(logger.handlers) == 0
    assert logger.name == "flask.app"
