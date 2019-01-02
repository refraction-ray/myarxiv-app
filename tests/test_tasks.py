from app.tasks import arxiv_query, arxiv_grab
import pytest

@pytest.mark.skip(reason="Avoid test this frequently due to the slow speed")
class TestTask:
    def test_create_task(app, db):
        t = arxiv_grab.run(['q-fin'])
        t = arxiv_query.run(search_mode=1, id_list=["1701.00001"])
        assert t == 1
