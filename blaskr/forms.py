from flaskext.wtf import Form, BooleanField, TextField, TextAreaField, PasswordField, validators, ValidationError, HiddenField, RecaptchaField
from models import *

class Unique(object):
    def __init__(self, model, field, message="This email has been used before"):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        if self.model.query.filter(self.field == field.data).first():
            raise ValidationError(self.message)

class Exists(object):
    def __init__(self, model, field, message = "We do not recognize that"):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        if not self.model.query.filter(self.field == field.data).first():
            raise ValidationError(self.message)
        
#this only works with our user class
class CheckPassword(object):
    def __init__(self, message = "That password does not match the one we have on record"):
        self.message = message

    def __call__(self, form, field):
        user = User.query.filter(User.email == form.email.data).first()
        if not user:
            return
        if not user.check_password(field.data):
            raise ValidationError(self.message)

class PostForm(Form):
    title = TextField("title", [validators.required()])
    text = TextAreaField("text")
    delete = BooleanField("delete post")
    post_id = HiddenField("post id")

class RegistrationForm(Form):
    email = TextField("email", [validators.Email(message="Not a valid email address")])
    username = TextField("username", [validators.Length(min=6), Unique(User, User.username)])
    password = PasswordField("Password", [
        validators.Required(),
        validators.EqualTo("Confirm", message="Passwords must match")
    ])
    confirm = PasswordField("Repeat Password")
    recaptcha = RecaptchaField()

class EditUserForm(Form):
    email = TextField("email", [validators.Length(min=6, max=35), validators.Email(message="Not a valid email address"), Unique(User, User.email)])
    password = PasswordField("New password", [
        validators.Required(),
        validators.EqualTo("confirm", message="Passwords must match")
    ])
    confirm = PasswordField("Confirm new password")


class LoginForm(Form):
    email = TextField("email", [validators.Required(), Exists(User, User.email, message="We do not recognize that email address")])
    password = PasswordField("password", [validators.Required(), CheckPassword()])

class CommentForm(Form):
    title = TextField("title", [validators.Required()])
    text = TextAreaField("text")
    post_id = HiddenField("post_id")
    comment_id = HiddenField("comment_id")
    delete = BooleanField("delete comment")
    recaptcha = RecaptchaField()
