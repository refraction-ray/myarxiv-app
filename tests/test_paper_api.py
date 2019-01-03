import logging


def test_paper_today(cache, db, caplog, client, auth):
    caplog.set_level(logging.INFO)
    r = client.get("/api/today")
    assert r.status_code == 200
    assert r.json.get("results")["first"] == 1
    assert isinstance(r.json.get("results")["items"], list)
    assert caplog.record_tuples[-1][2].startswith("set cache")  # no cache
    r = client.get("/api/today")
    assert caplog.record_tuples[-1][2].startswith("using")  # use cache
    with client: # the cache for login is different
        auth.login()
        r = client.get("/api/today")
        assert caplog.record_tuples[-1][2].startswith("set cache")
        r = client.get("/api/today")
        assert caplog.record_tuples[-1][2].startswith("using")


def test_cache_stateless(db, caplog, client):
    caplog.set_level(logging.INFO)
    r = client.get("/api/today")
    assert caplog.record_tuples[-1][2].startswith("set cache")
