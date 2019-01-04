import logging


def test_paper_today(cache, caplog, client, auth):
    caplog.set_level(logging.INFO)
    r = client.get("/api/today")
    assert r.status_code == 200
    assert r.json.get("results")["first"] == 1
    assert isinstance(r.json.get("results")["items"], list)
    assert caplog.record_tuples[-1][2].startswith("set cache")  # no cache
    r = client.get("/api/today")
    assert caplog.record_tuples[-1][2].startswith("using")  # use cache
    with client:  # the cache for login is different
        auth.login()
        r = client.get("/api/today")
        assert caplog.record_tuples[-1][2].startswith("set cache")
        r = client.get("/api/today")
        assert caplog.record_tuples[-1][2].startswith("using")


def test_cache_stateless(caplog, client):
    caplog.set_level(logging.INFO)
    r = client.get("/api/today")
    assert caplog.record_tuples[-1][2].startswith("set cache")


def test_paper_match(cache, client, auth):
    with client:
        auth.login()
        r = client.get("/api/today?date=20181217")
        assert r.json.get("results")["first"] == 1
        assert len(r.json.get("results")["items"][0]["keyword"]) == 2


def test_favorite_get(client, auth):
    with client:
        r = client.get("/api/favorites")
        assert r.json.get('message') == "Please log in first"
        auth.login()
        r = client.get("/api/favorites")
        assert r.json.get("results").get("has_next") == False
        assert len(r.json.get('results').get('items')) == 1
