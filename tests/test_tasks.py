from app.tasks import arxiv_query, arxiv_grab
import pytest

@pytest.mark.slow
class TestTask:
    def test_create_task(client, db):
        t = arxiv_grab.run(['q-fin'])
        t = arxiv_query.run(search_mode=1, id_list=["1701.00001"])
        assert t == 1

