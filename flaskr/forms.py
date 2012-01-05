from wtforms import Form, BooleanField, TextField, TextAreaField, PasswordField, validators, ValidationError
from models import *

class Unique(object):
    def __init__(self, model, field, message="must be unique"):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        if self.model.query.filter(self.field == field.data).first():
            raise ValidationError(self.message)


class PostForm(Form):
    title = TextField('title', [validators.required()])
    text = TextAreaField('text')


class RegistrationForm(Form):
    email = TextField('email', [validators.Length(min=6, max=35), Unique(User, User.email)])
    password = PasswordField('password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    email = TextField('email', [validators.Required()])
    password = PasswordField('password', [validators.Required()])
