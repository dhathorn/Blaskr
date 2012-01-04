from flaskext.sqlalchemy import SQLAlchemy
from datetime import datetime
from flaskr import db

#models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.String(180))

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return '<Title %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String())
    activate = db.Column(db.Boolean)
    created = db.Column(db.DateTime)
    role = db.Column(db.String(15))

    def __init__(self, email, password, role='User'):
       self.email = email
       self.password = generate_password_hash(password)
       self.activate = True #FIXME
       self.created = datetime.utcnow()
       self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<email %r>' % self.email


