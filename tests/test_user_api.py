from flask_login import current_user
from app.security import ts, tscf
from app.models import UserInfo


def test_correct_login(client, auth):
    with client:
        r = auth.login()
        assert current_user.email == "test@test.com"
        assert r.json.get('state') == 'success'
        assert current_user.is_authenticated is True
        r = auth.logout()
        assert r.headers['Location'] == 'http://localhost/login'


def test_wrong_login(client, auth):
    with client:
        r = auth.login(password="")
        assert r.status_code == 422
        assert r.json.get('message') == "Incorrect input in the form"
        r = auth.login(password="123456")
        assert r.status_code == 422
        assert r.json.get('message') == "The password or email is incorrect"
        assert current_user.is_authenticated is False
        r = auth.logout()
        assert r.status_code == 302
        # assert r.headers['Location'] == 'http://localhost/login?next=%2Fapi%2Flogout'
        r = auth.logout()
        assert r.status_code == 302 # logout of no user doesn't lead to problems


def test_correct_register(client, auth):
    with client:
        r = client.post(
            '/api/registration', data={'name': 'test101', 'email': 'test101@test.com', 'password': 'testtest'})
        assert r.json.get('message') == "the user is successfully created"
        r = auth.login(email='test101@test.com', password='testtest')
        assert current_user.is_authenticated is True
        r = auth.logout()


def test_wrong_register(client, auth):
    with client:
        r = auth.login(email='test101@test.com', password='testtest')
        assert current_user.is_authenticated is False
        r = client.post(
            '/api/registration', data={'name': 'test', 'email': 'test101@test.com', 'password': 'testtest'})
        assert r.json.get('message') == "The username has already been used."
        r = client.post(
            '/api/registration', data={'name': 'test', 'email': 'test.com', 'password': 'testtest'})
        assert r.json.get('message') == "Incorrect input in the form"
        r = client.post(
            '/api/registration', data={'name': 'test', 'mail': 'test.com', 'password': 'testtest'})
        assert r.json.get('message') == "Incorrect input in the form"


def test_keywords_post(client, auth):
    with client:
        auth.login()
        ctoken = tscf.dumps(current_user.id)
        ctoken_wrong = ts.dumps(current_user.id)
        r = client.post("/api/keywords",
                        json={"ctoken": ctoken, "items":
                            [{"keyword": "quantum computation", "weight": 10}]})
        assert r.json.get('state') == "success"
        r = client.post("/api/keywords",
                        json={"ctoken": ctoken_wrong, "items":
                            [{"keyword": "quantum computation", "weight": 10}]})
        assert r.json.get('message') == "The token was expired, please reload the page."
        r = client.get('/api/keywords')
        assert r.json.get("results")[0]['weight'] == 10
        assert len(r.json.get("results")) == 1
        r = client.post("/api/keywords",
                        json={"ctoken": ctoken[2:] + "x", "items":
                            [{"keyword": "quantum computation", "weight": 10}]})
        assert r.json.get('message') == "The token was expired, please reload the page."


def test_keywords_get(client, auth):
    with client:
        auth.login()
        r = client.get('/api/keywords')
        assert r.json.get("results")[1]['keyword'] == "machine learning"
        auth.logout()
        r = client.get('/api/keywords')
        assert r.status_code == 403


def test_fields_post(client, auth):
    with client:
        auth.login()
        ctoken = tscf.dumps(current_user.id)
        r = client.get("/api/fields")
        assert r.json.get("quant-ph") is True
        r = client.post("/api/fields", json={
            "fields": [{"abbr": "cond-mat", "checked": True}]})
        assert r.json.get("message") == "The token was expired, please reload the page."
        r = client.post("/api/fields", json={
            "ctoken": ctoken, "fields": [{"abbr": "cond-mat", "checked": True}]})
        assert r.json.get("message") == "the interest fields are successfully updated"
        r = client.get("/api/fields")
        assert r.json.get("cond-mat") is True
        assert r.json.get("quant-ph") is False
        assert r.json.get("cond-mat.str-el") is None


def test_userinfo_post(client, auth, db):
    with client:
        auth.login()
        ctoken = tscf.dumps(current_user.id)
        r = client.post("/api/userinfo", data={"dailymail": True})
        r = client.post("/api/userinfo", data={"ctoken": ctoken, "dailymail": True})
        assert r.json.get("message") == "Incorrect input in the form"
        r = client.post("/api/userinfo", data={"ctoken": ctoken, "dailymail": True,
                                               "imgurl": "http://www.example.com/figure.jpg", "profile": "nb!"})
        assert r.json.get("message") == "the user info is successfully updated"
        r = client.get("/api/userinfo")
        assert r.json.get("dailymail") is False  # unverified user cannot subscribe on mails
        assert r.json.get("profile") == "nb!"
        ui = UserInfo.query.filter_by(uid=current_user.id).first()
        ui.verified = True
        db.session.commit()
        r = client.post("/api/userinfo", data={"ctoken": ctoken, "dailymail": False,
                                               "imgurl": "http://www.example.com/figure.jpg", "profile": "nb!!"})
        assert r.json.get('state') == "success"
        r = client.get("/api/userinfo")
        assert r.json.get("profile") == "nb!!"
        assert r.json.get("verified") is True
        assert r.json.get("dailymail") is False


def test_password_reset(client):
    with client:
        r = client.post("/api/password/reset", data={"email": "test@test.net"})
        assert r.json.get('message') == "No user use this email address"
        r = client.post("/api/password/reset", data={"email": "test@test.com"})
        assert r.json.get('message') == 'The email isn\'t verified, so you cannot reset the password'


def test_password_edit(client, auth, db):
    with client:
        auth.login()
        ctoken = tscf.dumps(current_user.id)
        r = client.post("/api/password/edit", data={ "ctoken": ctoken,
            "email": "test@test.com", "password": "123456"})
        assert r.json.get('message') == "Don't try to do something weird"
        ui = UserInfo.query.filter_by(uid=current_user.id).first()
        ui.verified = True
        db.session.commit()
        r = client.post("/api/password/edit", data={"ctoken": ctoken,
                                                    "email": "test@test.com", "password": "123456"})
        assert r.json.get('message') == "the password is successfully changed"

def test_nochange_password(client, auth):
    with client:
        auth.login()
        assert current_user.id == 1