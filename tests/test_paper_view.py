def test_index(client):
    r = client.get("/")
    assert r.status_code == 200

def test_paper_page(client):
    r = client.get("/paper/1812.35598")
    assert r.status_code == 200