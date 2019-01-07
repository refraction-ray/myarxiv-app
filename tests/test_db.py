from app.models import Author
from app.models import db as dbtest


def test_basics(db):
    a = Author(pid=3, author="Foo Bar", authorrank=10)
    db.session.add(a)
    db.session.flush()
    assert dbtest.session == db.session  # the session from models is the same as pytest.fixture
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
    db.session.rollback()  # rollback is just a pass if there is no progress
    a = Author.query.filter_by(author="Foo Bar").first()
    assert a.pid == 3


def test_stateless():
    a = Author.query.filter_by(author="Foo Bar").first()
    assert a is None
    a = Author.query.filter_by(id=2).first()
    assert a.pid == 1


def test_modelmixin():
    assert Author.getone(1).author == 'Mucong Ding'
    assert len(Author.gets(pid=1)) == 2
    assert Author.getpage(nums=2).has_next == True
    a = Author(pid=2, author="Foo Bar Go", authorrank=10)
    a.save(True)
    assert Author.get(authorrank=10).pid == 2
    a.update(pid=3)
    assert Author.get(authorrank=10).pid == 3
