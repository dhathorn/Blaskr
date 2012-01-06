import os
import flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        flaskr.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/flaskr_test.db"
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        self.db = flaskr.init_db(flaskr.app)
        self.db.drop_all()
        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()

    def register(self, un, pw, conf):
        return self.app.post("/register", data=dict(email=un, password=pw, confirm=conf))

    def login(self, un, pw):
        return self.app.post("/login", data=dict(email=un, password=pw))

    def logout(self):
        return self.app.get("/logout")

    def test_empty_db(self):
        rv = self.app.get('/')
        assert "No entries here so far" in rv.data

    def test_login_logout(self):
        rv = self.register("eggs@yahoo.com", "spammmmm", "cam")
        assert "Passwords must match" in rv.data
        rv = self.register("eggs", "spammmmm", "spammmmm")
        assert "Not a valid email address" in rv.data
        rv = self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        assert "Account created" in rv.data
        rv = self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        assert "Email must be unique" in rv.data
        rv = self.login("eggo", "s:(")
        assert "We don't recognize that username" in rv.data
        rv = self.login("eggs@yahoo.com", "spam")
        assert "Incorrect password" in rv.data
        rv = self.login("eggs@yahoo.com", "spammmmm")
        assert "logged in" in rv.data
        rv = self.logout()
        assert "logged out" in rv.data

    def test_post(self):
        rv = self.app.post("/post/add", data=dict(title="test", text="test"))
        assert rv.status_code == 401
        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")
        rv = self.app.post("/post/add", data=dict(title="test", text="test"))
        assert "successfully posted" in rv.data

    def edit_post(self):
        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")
        rv = self.app.post("/post/add", data=dict(title="test", text="test"))

    def test_add_comment(self):
        rv = self.app.post("/comment/add", data=dict(title="test", text="test"))
        assert "successfully posted" in rv.data
        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")
        rv = self.app.post("/comment/add", data=dict(title="test", text="test"))
        assert "successfully posted" in rv.data



if __name__ == '__main__':
    unittest.main()
