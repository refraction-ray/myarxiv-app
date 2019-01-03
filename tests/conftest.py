import os
import pytest
from app.main import create_app
from app.models import db as db_test
from sqlalchemy import event
import logging
import sys
from app.cache import cache as cache_test
from app.helper import get_config


testconf = get_config(name="config_test.yaml", override="config_test_override.yaml",
                      path=os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=getattr(logging, testconf.get('TEST_LOGGING_LEVEL', 'WARNING'), None), stream=sys.stdout)


def init_db():
    prefix = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(prefix, "init.sql"), "r") as sql:
        command = ""
        for line in sql:
            if line.strip():
                if not line.startswith("--"):
                    line = line.strip()
                    command += line
                    if line[-1] != ";":
                        continue
                    else:
                        # print("The command to be run is: " + command)
                        db_test.engine.execute(command)
                        command = ""


@pytest.fixture(scope='session')
def app():
    app = create_app(True, False, testconf=testconf)

    with app.app_context():
        init_db()
        yield app
        cache_test.clear()  # ensure cache is clear in case there is error quit of related test functions


@pytest.fixture(scope='function')
def db(app):
    connection = db_test.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db_test.create_scoped_session(options=options)
    session.begin_nested()
    db_test.session = session

    @event.listens_for(db_test.session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            # ensure that state is expired the way
            # session.commit() at the top level normally does
            # (optional step)
            session.expire_all()
            session.begin_nested()

    # db_test.init_app(current_app)
    yield db_test
    session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def cache(app):
    yield cache_test
    cache_test.clear()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email='test@test.com', password="ca6d24d11167b2ed0a90b3e831d3a8fb026d9b9d"):
        return self._client.post(
            '/api/login',
            data={'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/api/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
