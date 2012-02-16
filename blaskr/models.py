from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from flaskext.login import UserMixin
from flaskext.sqlalchemy import SQLAlchemy
from flask import session
db = SQLAlchemy()

#models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.String(180))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("posts", lazy = "dynamic"))

    def owner(self, user):
        return user == self.user

    def __init__(self, title, text, user_id):
        self.title = title
        self.text = text
        self.user_id = user_id

    def __repr__(self):
        return "<Title %r>" % self.title

    def owner_string(self):
        return User.query.get(self.user_id).email


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.String(180))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post = db.relationship("Post", backref=db.backref("comments", lazy = "dynamic"))
    user = db.relationship("User", backref=db.backref("comments", lazy = "dynamic"))

    def owner(self, user):
        "Owner can be either the comment owner, or the user who owns the parent post"
        return self.user == user or self.post.user == user

    def __init__(self, title, text, post_id, user_id=0):
        self.title = title
        self.text = text
        self.post_id = post_id
        self.user_id = user_id

    def owner_string(self):
        return self.user_id and User.query.get(self.user_id).email or "Anonymous"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String())
    activate = db.Column(db.Boolean)
    created = db.Column(db.DateTime)
    role = db.Column(db.Integer) #1 is admin, 10 is user, 20 is commentator
    roles = {"Admin" : 1, "Member" : 10, "Commenter" : 20}

    def owner(self, user):
        return self.id == user.id

    def __init__(self, email, password, role=20):
       self.email = email
       self.password = generate_password_hash(password)
       self.activate = True #FIXME
       self.created = datetime.utcnow()
       self.role = self.role_number(role)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<email %r>" % self.email

    #helper function
    def role_number(self, role):
        if type(role) == int:
            return role
        return self.roles.get(role)

    def is_authorized(self, for_role):
        return self.role <= self.role_number(for_role)
