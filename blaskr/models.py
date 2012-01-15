from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from blaskr import db
from flaskext.login import UserMixin
from flask import session

#models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.String(180))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("posts", lazy = "dynamic"))

    def __init__(self, title, text, user_id):
        self.title = title
        self.text = text
        self.user_id = user_id

    def __repr__(self):
        return "<Title %r>" % self.title

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.String(180))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post = db.relationship("Post", backref=db.backref("comments", lazy = "dynamic"))
    user = db.relationship("User", backref=db.backref("comments", lazy = "dynamic"))

    def __init__(self, title, text, post_id, user_id=0):
        self.title = title
        self.text = text
        self.post_id = post_id
        self.user_id = user_id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String())
    activate = db.Column(db.Boolean)
    created = db.Column(db.DateTime)
    role = db.Column(db.String(15))

    def __init__(self, email, password, role="User"):
       self.email = email
       self.password = generate_password_hash(password)
       self.activate = True #FIXME
       self.created = datetime.utcnow()
       self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<email %r>" % self.email
