from app.tasks import arxiv_query, arxiv_grab
from app.models import Paper
import pytest
import time


@pytest.mark.slow
class TestTask:
    def test_create_task(self, celery_worker, celery_app):
        t = arxiv_grab.run(['q-fin'])
        t = arxiv_query.delay(search_mode=1, id_list=["1701.00001"])
        assert t.get() == 1
        t.forget()

    def test_download_api(self, client, celery_worker, celery_app):
        r = client.post("/api/download", json={"search_mode": 1, "id_list": ["1701.00001"]})
        assert r.json.get('status') == "accepted"
        tid = r.json.get('taskid')
        r = client.get('/api/status/' + tid)
        tries = 0
        while r.json.get('state') == -1 and tries < 20:
            time.sleep(2)
            tries += 1
            r = client.get('/api/status/' + tid)
        assert r.json.get('state') == 1
        celery_app.AsyncResult(tid).forget()
        assert Paper.get(arxivid="1701.00001")
