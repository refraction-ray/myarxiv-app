def test_config(app):
    assert app.config["TESTING"] is True
