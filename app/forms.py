"""
forms definition for the app
"""

from wtforms import Form, StringField, validators, BooleanField


class EmailForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=60), validators.Email()])


class LoginForm(EmailForm):
    password = StringField('Password', [validators.Length(min=6, max=40)])  # there is actually a builtin password.field


class RegistrationForm(LoginForm):
    name = StringField('Username', [validators.Length(min=3, max=30)])


class UserInfoForm(Form):
    imgurl = StringField('imgurl', [validators.URL(), validators.Length(min=5, max=512)])
    dailymail = BooleanField('dailymail', false_values=["False", "false", "0"])
    profile = StringField('profile')

"""
class QueryForm(Form):
    default_keywords = BooleanField('default_keywords', default=True)
    default_subjects = BooleanField('default_subjects', default=True)
    keywords = FieldList(StringField('keywords'), default=[])
    subjects = FieldList(StringField('subjects'), default=[])
    authors = FieldList(StringField('authors'), default=[])
    page = IntegerField('page', default=1)
    limit = IntegerField('limit', default=10)
    favorites = BooleanField('favorites', default=False)
"""
