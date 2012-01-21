#!/usr/bin/python
import blaskr
import unittest
from flask import Flask
from blaskr.models import *

class MyTest(unittest.TestCase):
    def setUp(self):
        blaskr.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        blaskr.app.config['TESTING'] = True
        blaskr.app.config['DEBUG'] = False
        blaskr.app.config['CSRF_ENABLED'] = False
        blaskr.app.test_request_context().push()
        blaskr.db.create_all()
        self.app = blaskr.app.test_client()

    def tearDown(self):
        blaskr.db.drop_all()

    def register(self, un, pw, conf):
        return self.app.post("/register", data=dict(email=un, password=pw, confirm=conf, recaptcha_challenge_field='test',
                                                                               recaptcha_response_field= 'test'), follow_redirects=True)

    def change_role(self, user_id, role):
        user = User.query.get(user_id)
        user.role = role
        db.session.commit()

    def login(self, un, pw):
        return self.app.post("/login", data=dict(email=un, password=pw), follow_redirects=True)


    def logout(self):
        return self.app.get("/logout", follow_redirects=True)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert "No entries here so far" in rv.data

    def test_login_logout(self):
        rv = self.app.get("/register")
        assert rv.status_code == 200
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
        assert rv.status_code == 404
        rv = self.app.post("/post/1", data=dict(method="DELETE"), follow_redirects=True)
        assert rv.status_code == 404

        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")
        self.change_role(1, "User")

        rv = self.app.post("/post/add", data=dict(title="test", text="magic baked in right here"), follow_redirects=True)
        assert "New entry was successfully posted" in rv.data
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

        rv = self.app.post("/post/add", data=dict(title="test", text="magic baked in right here"), follow_redirects=True)
        self.logout()

        rv = self.app.post("/post/1", data=dict(title="editing", text="this"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)
        rv = self.app.post("/post/1", data=dict(method="DELETE"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)

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

        rv = self.app.post("/comment/add", data=dict(title="test", text="anon", post_id=1, recaptcha_challenge_field='test',
                                                                 recaptcha_response_field= 'test'), follow_redirects=True)
        assert "Successfully added" in rv.data
        rv = self.app.get("/comment/1", follow_redirects=True)
        assert "anon" in rv.data
        rv = self.app.post("/comment/add", data=dict(title="test", text="anon", post_id=2, recaptcha_challenge_field='test',
                                                                 recaptcha_response_field= 'test'), follow_redirects=True)
        assert rv.status_code == 403
        rv = self.app.post("/comment/1", data=dict(title="edited", text="anon", post_id=1), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)
        rv = self.app.post("/comment/1", data=dict(method="DELETE"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Please log in" in rv.data)

    def test_post_comment_owner(self):
        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")
        self.change_role(1, "User")
        rv = self.app.post("/post/add", data=dict(title="test", text="magic baked in right here"), follow_redirects=True)
        assert "by eggs@yahoo.com" in rv.data
        rv = self.app.post("/comment/add", data=dict(title="test", text="magic", post_id=1), follow_redirects=True)
        assert "by eggs@yahoo.com" in rv.data

        self.logout()

        rv = self.app.post("/comment/add", data=dict(title="test", text="anon", post_id=1, recaptcha_challenge_field='test',
                                                                 recaptcha_response_field= 'test'), follow_redirects=True)
        assert "by Anonymous" in rv.data
        
    def test_authorization(self):
        self.register("eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("eggs@yahoo.com", "spammmmm")
        self.change_role(1, "User")
        rv = self.app.post("/post/add", data=dict(title="post", text="to test comments"), follow_redirects=True)
        rv = self.app.post("/comment/add", data=dict(title="new", text="comment", post_id=1), follow_redirects=True)
        self.logout()
        self.register("more_eggs@yahoo.com", "spammmmm", "spammmmm")
        self.login("more_eggs@yahoo.com", "spammmmm")

        rv = self.app.post("/comment/1", data=dict(title="edited", text="anon", post_id=1), follow_redirects=True)
        assert (rv.status_code == 401) or ("Not authorized" in rv.data)
        rv = self.app.post("/comment/1", data=dict(method="DELETE"), follow_redirects=True)
        assert (rv.status_code == 401) or ("Not authorized" in rv.data)

    def test_captcha(self):
        pass

    def test_pagination(self):
        pass

    def test_edit_count(self):
        pass

if __name__ == "__main__":
    unittest.main()
