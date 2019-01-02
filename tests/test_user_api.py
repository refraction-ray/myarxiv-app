from flask_login import current_user


def test_correct_login(client, auth, db):
    with client:
        r = auth.login()
        assert r.json.get('state') == 'success'
        assert current_user.is_authenticated is True
        r = auth.logout()
        assert r.headers['Location'] == 'http://localhost/login'


def test_wrong_login(client, auth, db):
    with client:
        r = auth.login(password="")
        assert r.status_code == 422
        assert r.json.get('message') == "Incorrect input in the form"
        r = auth.login(password="123456")
        assert r.status_code == 422
        assert r.json.get('message') == "The password or email is in correct"
        assert current_user.is_authenticated is False
        r = auth.logout()
        assert r.status_code == 302
        assert r.headers['Location'] == 'http://localhost/login?next=%2Fapi%2Flogout'

def test_correct_register(client, auth, db):
    with client:
        r = client.post(
        '/api/registration', data={'name': 'test101', 'email':'test101@test.com','password': 'testtest'})
        assert r.json.get('message') == "the user is successfully created"
        r = auth.login(email='test101@test.com',password='testtest')
        assert current_user.is_authenticated is True
        r = auth.logout()

def test_wrong_register(client, auth, db):
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