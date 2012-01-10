import flaskr
import unittest
from flask import Flask
from flaskr import db, init_db
from flaskr.models import *

class MyTest(unittest.TestCase):
    def setUp(self):
        flaskr.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        flaskr.app.config['TESTING'] = True
        flaskr.db.create_all()
        self.app = flaskr.app.test_client()

    def tearDown(self):
        flaskr.db.drop_all()

    def register(self, un, pw, conf):
        return self.app.post("/register", data=dict(email=un, password=pw, confirm=conf), follow_redirects=True)

    def login(self, un, pw):
        return self.app.post("/login", data=dict(email=un, password=pw), follow_redirects=True)

    def logout(self):
        return self.app.get("/logout", follow_redirects=True)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert "No entries here so far" in rv.data

    def test_login_logout(self):
        rv = self.register("eggs@yahoo.com", "spammmmm", "cam")
        assert "Passwords must match" in rv.data
        rv = self.register("eggggggggggggs", "spammmmm", "spammmmm")
        assert "Not a valid email address" in rv.data
        rv = self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        assert "Account created" in rv.data
        rv = self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        assert "This email has been used before" in rv.data
        rv = self.login("eggo", "s:(")
        assert "We do not recognize that email" in rv.data
        rv = self.login("eggs@yahoo.com", "spam")
        assert "That password does not match the one we have on record" in rv.data
        rv = self.login("eggs@yahoo.com", "spammmmm")
        assert "logged in" in rv.data
        rv = self.logout()
        assert "logged out" in rv.data

    def test_post(self):
        rv = self.app.get("/post/1")
        assert rv.status_code == 404
        rv = self.app.post("/post/add", data=dict(title="test", text="test"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)
        rv = self.app.post("/post/1", data=dict(title="editing", text="this"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)
        rv = self.app.post("/post/1", data=dict(method="DELETE"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)

        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")

        rv = self.app.post("/post/add", data=dict(title="test", text="magic baked in right here"), follow_redirects=True)
        assert "Successfully posted post" in rv.data
        rv = self.app.get("/post/1")
        assert "magic baked in right here" in rv.data
        rv = self.app.post("/post/1", data=dict(title="test", text="no more magic!"), follow_redirects=True)
        assert "Successfully edited post" in rv.data
        rv = self.app.get("/post/1")
        assert "no more magic" in rv.data
        rv = self.app.post("/post/1", data=dict(method="DELETE"), follow_redirects=True)
        assert "Successfully deleted post" in rv.data
        rv = self.app.get("/post/1")
        assert rv.status_code == 404 


    def test_comment(self):
        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")
        rv = self.app.post("/post/add", data=dict(title="post", text="to test comments"), follow_redirects=True)

        rv = self.app.post("/comment/add", data=dict(title="test", text="magic", post_id=1), follow_redirects=True)
        assert "Successfully added" in rv.data
        rv = self.app.post("/comment/add", data=dict(title="test", text="magic", post_id=2), follow_redirects=True)
        assert rv.status_code == 403
        rv = self.app.post("/comment/add", data=dict(title="test", text="magic"), follow_redirects=True)
        assert rv.status_code == 403
        rv = self.app.post("/comment/1", data=dict(title="test", text="more magic"), follow_redirects=True)
        assert "Successfully edited" in rv.data
        rv = self.app.post("/comment/1", data=dict(method="DELETE"), follow_redirects=True)
        assert "Successfully deleted" in rv.data 
        rv = self.app.get("/comment/1")
        assert rv.status_code == 404

        self.logout()

        rv = self.app.post("/comment/add", data=dict(title="test", text="anon", post_id=1), follow_redirects=True)
        assert "Successfully added" in rv.data
        rv = self.app.post("/comment/add", data=dict(title="test", text="anon", post_id=2), follow_redirects=True)
        assert rv.status_code == 403
        rv = self.app.post("/comment/1", data=dict(title="edited", text="anon", post_id=1), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)
        rv = self.app.post("/comment/1", data=dict(method="DELETE"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)

if __name__ == "__main__":
    unittest.main()
