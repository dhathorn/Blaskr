from wtforms import Form, BooleanField, TextField, PasswordField, validators

class RegistrationForm(Form):
    email = TextField('email', [validators.Length(min=6, max=35)])
    pwd = PasswordField('pwd', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
