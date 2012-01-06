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
        rv = self.app.get("/post/1")
        assert rv.status_code == 404
        rv = self.app.post("/post/add", data=dict(title="test", text="test"), follow_redirects=True)
        assert rv.status_code == 401
        rv = self.app.post("/post/1", data=dict(title="editing", text="this"), follow_redirects=True)
        assert rv.status_code == 401
        rv = self.app.post("/post/1", data=dict(method="DELETE"), follow_redirects=True)
        assert rv.status_code == 401

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
        assert "Post doesn't exsist" in rv.data
        rv = self.app.post("/comment/1", data=dict(title="test", text="more magic", post_id=1), follow_redirects=True)
        assert "Successfully edited" in rv.data
        rv = self.app.post("/comment/1", data=dict(title="test", text="more magic", post_id=2), follow_redirects=True)
        assert "Cannot change comment parent" in rv.data
        rv = self.app.post("/comment/1", data=dict(method="DELETE"), follow_redirects=True)
        assert "Successfully deleted" in rv.data 
        rv = self.app.get("/comment/1")
        assert rv.status_code == 404

        self.logout

        rv = self.app.post("/comment/add", data=dict(title="test", text="anon", post_id=1), follow_redirects=True)
        assert "successfully added" in rv.data
        rv = self.app.post("/comment/add", data=dict(title="test", text="anon", post_id=2), follow_redirects=True)
        assert "Post doesn't exsist" in rv.data
        rv = self.app.post("/comment/1", data=dict(title="edited", text="anon", post_id=1), follow_redirects=True)
        assert rv.status_code == 401 
        rv = self.app.post("/comment/1", data=dict(method="DELETE"), follow_redirects=True)
        assert rv.status_code == 401 

if __name__ == '__main__':
    unittest.main()
