from app.models import Author
from app.models import db as dbtest


def test_basics(db):
    a = Author(pid=3, author="Foo Bar", authorrank=10)
    db.session.add(a)
    db.session.flush()
    assert dbtest.session == db.session # the session from models is the same as pytest.fixture
    a = Author.query.filter_by(author="Foo Bar").first()
    assert a.pid == 3  # the item is already inserted into database by flush()
    db.session.rollback()  # rollback to the beginning since no commit
    a = Author.query.filter_by(author="Foo Bar").first()
    assert a is None
    a = Author(pid=3, author="Foo Bar", authorrank=10)
    db.session.add(a)
    db.session.commit()
    db.session.rollback()
    a = Author.query.filter_by(author="Foo Bar").first()
    assert a.pid == 3
    db.session.rollback()
    db.session.rollback() # rollback is just a pass if there is no progress
    a = Author.query.filter_by(author="Foo Bar").first()
    assert a.pid == 3


def test_stateless(db):
    a = Author.query.filter_by(author="Foo Bar").first()
    assert a is None
    a = Author.query.filter_by(id=2).first()
    assert a.pid == 1
