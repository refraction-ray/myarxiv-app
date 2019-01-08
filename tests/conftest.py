import os
import pytest
import logging
import sys
from sqlalchemy import event
from contextlib import contextmanager
from celery.contrib.testing.worker import TestWorkController, setup_app_for_worker

from app.main import create_app
from app.models import db as db_test
from app.cache import cache as cache_test
from app.helper import get_config
from app.tasks import celery as celery_test

testconf = get_config(name="config_test.yaml", override="config_test_override.yaml",
                      path=os.path.dirname(os.path.abspath(__file__)))

log_level = testconf.get('TEST_LOGGING_LEVEL', 'WARNING')

logging.basicConfig(level=getattr(logging, log_level, None), stream=sys.stdout)


def init_db(db_test):
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


def drop_db(db_test):
    prefix = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(prefix, "init.sql"), "r") as sql:
        for lno, line in enumerate(sql):
            if line.strip().startswith("DROP TABLE") or lno < 10:
                line = line.strip()
                # print(line)
                db_test.engine.execute(line)


@pytest.fixture(scope='session')
def app():
    app = create_app(True, False, testconf=testconf)
    with app.app_context():
        celery_test.conf.update(app.config)
        init_db(db_test)
        cache_test.clear()
        yield app
        cache_test.clear()  # ensure cache is clear in case there is error quit of related test functions
        connection = db_test.engine.connect()
        options = dict(bind=connection, binds={})
        session = db_test.create_scoped_session(options=options)
        db_test.session = session
        drop_db(db_test)
        celery_test.control.purge()


@pytest.fixture(scope='function', autouse=True)
def db(app):
    """
    This function should be implicitly called for each test, since the db is closed each time
    """
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


def pytest_addoption(parser):
    parser.addoption('--all', action='store_true',
                     default=False, help="enable longrundecorated tests")


def pytest_collection_modifyitems(config, items):
    """
    if -all not specified, the test functions makrd by slow is omitted
    """
    if config.getoption("--all"):
        return
    skip_slow = pytest.mark.skip(reason="need --all option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {"perform_ping_check": False}


@pytest.fixture(scope='session')
def celery_app(app):
    return celery_test


"""
the set of functions below is an ugly hack on celery.testing module,
somehow the original module is broken to run the test due to some meaningless check,
at least to celery 4.2.1.
in this hack version, the connection check is simply removed,
and everything is fine in pytest
"""


@pytest.fixture()
def celery_worker(request,
                  celery_app,
                  celery_includes,
                  celery_worker_pool,
                  celery_worker_parameters):
    for module in celery_includes:
        celery_app.loader.import_task_module(module)
    with start_worker(celery_app,
                      pool=celery_worker_pool,
                      **celery_worker_parameters) as w:
        yield w


@contextmanager
def start_worker(app,
                 concurrency=1,
                 pool='solo',
                 loglevel=log_level,  #
                 logfile=None,
                 **kwargs):
    from celery.utils.dispatch import Signal

    test_worker_starting = Signal(
        name='test_worker_starting',
        providing_args={},
    )
    test_worker_stopped = Signal(
        name='test_worker_stopped',
        providing_args={'worker'},
    )
    test_worker_starting.send(sender=app)

    with _start_worker_thread(app,
                              concurrency=concurrency,
                              pool=pool,
                              loglevel=loglevel,
                              logfile=logfile,
                              **kwargs) as worker:
        yield worker

    test_worker_stopped.send(sender=app, worker=worker)


@contextmanager
def _start_worker_thread(app,
                         concurrency=1,
                         pool='solo',
                         loglevel=log_level,
                         logfile=None,
                         WorkController=TestWorkController,
                         **kwargs):
    from celery.utils.nodenames import anon_nodename
    from celery.result import _set_task_join_will_block
    import threading

    setup_app_for_worker(app, loglevel, logfile)

    worker = WorkController(
        app=app,
        concurrency=concurrency,
        hostname=anon_nodename(),
        pool=pool,
        loglevel=loglevel,
        logfile=logfile,
        ready_callback=None,
        without_heartbeat=True,
        without_mingle=True,
        without_gossip=True,
        **kwargs)

    t = threading.Thread(target=worker.start)
    t.start()
    worker.ensure_started()
    _set_task_join_will_block(False)

    yield worker

    from celery.worker import state
    state.should_terminate = 0
    t.join(10)
    state.should_terminate = None