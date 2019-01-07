from app.security import ts
from app.models import UserInfo
from flask_login import current_user
import pytest


def test_register_view(client, auth):
    with client:
        r = client.get("/register")
        assert r.status_code == 200
        auth.login()
        r = client.get("/register")
        assert r.status_code == 302


def test_login_view(client, auth):
    with client:
        r = client.get("/login")
        assert r.status_code == 200
        auth.login()
        r = client.get("/login")
        assert r.status_code == 302


@pytest.mark.parametrize("url", [
    "/settings/userinfo", "/settings/keywords", "/password/reset"
])
def test_general_view(client, auth, url):
    with client:
        auth.login()
        r = client.get(url)
        assert r.status_code == 200
        assert r.content_type == "text/html; charset=utf-8"


def test_confirm_token(client):
    with client:
        token = ts.dumps("test@test.com")
        r = client.get("/confirm/" + token)
        assert r.headers['location'][-8:] == "userinfo"
        ui = UserInfo.query.filter_by(uid=1).first()
        assert ui.verified is True
        r = client.get("/confirm/" + token[:-2] + "mm")
        assert r.status_code == 404


def test_reset_token(client):
    with client:
        token = ts.dumps("test@test.com")
        r = client.get("/reset/" + token)
        assert current_user.id == 1
        assert r.status_code == 200
        r = client.get("/reset/" + token[:-1])
        assert r.status_code == 404
