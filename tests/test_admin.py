from flask_login import current_user

def test_admin_access(client, auth):
    with client:
        r = client.get("/admin/")
        assert r.status_code == 404
        auth.login()
        r = client.get("/admin/")
        assert r.status_code == 404
        current_user.update(admin=True)
        r = client.get("/admin/")
        assert r.status_code == 200
