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


def test_correct_query(client, auth):
    with client:
        r = client.post("/api/query", json={"dates": ["2018-12-17"]})
        assert len(r.json.get('results')['items']) == 3
        r = client.post("/api/query", json={"dates": ["2019-12-17"]})
        assert r.json.get('results')['last'] == 1
        assert r.json.get('results')['nums'] == 10
        auth.login()
        r = client.post("/api/query", json={"dates": ["2018-12-17","2019-12-31"],
                                            "default_subjects": True,
                                            "default_keywords": True,
                                            "keywords": ["brain"]})
        assert r.status_code == 200
        assert len(r.json.get('results')['items'][0]['keyword']) == 3
        r = client.post("/api/query", json={"dates": ["2018-12-17","2019-12-31"],
                                            "favorites": True})
        assert len(r.json.get('results')['items']) == 1
