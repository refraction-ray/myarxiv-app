"""
forms definition for the app
"""

from wtforms import Form, StringField, validators, BooleanField


class EmailForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=60), validators.Email()])


class LoginForm(EmailForm):
    password = StringField('Password', [validators.Length(min=6, max=40)])


class RegistrationForm(LoginForm):
    name = StringField('Username', [validators.Length(min=3, max=30)])


class UserInfoForm(Form):
    imgurl = StringField('imgurl', [validators.URL(), validators.Length(min=5, max=512)])
    dailymail = BooleanField('dailymail')
    profile = StringField('profile')
