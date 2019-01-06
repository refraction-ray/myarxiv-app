from flask import (Blueprint, request, jsonify, url_for, current_app,
                   render_template, abort, redirect)
from ..models import User, db, UserInfo
from ..exceptions import *
from ..forms import RegistrationForm, LoginForm
from flask_login import current_user, login_required
from flask_login import login_user
from itsdangerous import BadData

userview = Blueprint('userview', __name__)


@userview.after_app_request  # add http headers for all request even outside the blueprint
def add_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Server'] = ""
    return response


@userview.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    return render_template("register.html", form=form, register=True)


@userview.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    return render_template("register.html", form=form, register=False)


@userview.route('/settings/keywords')
@login_required
def settings_keywords():
    return render_template("keywords.html", token=current_user.id)


@userview.route('/settings/userinfo')
@login_required
def settings_userinfo():
    return render_template("userinfo.html", token=current_user.id)


@userview.route("/confirm/<token>")
def confirm(token):
    try:
        email = ts.loads(token, max_age=86400)
    except BadData:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()
    ui = UserInfo.query.filter_by(uid=user.id).first_or_404()
    ui.verified = True
    db.session.commit()

    return redirect(url_for("userview.settings_userinfo"))


@userview.route("/password/reset")
def password_reset():
    return render_template("passwordreset.html", before=True, token="")


@userview.route("/reset/<token>")
def reset_token(token):
    try:
        email = ts.loads(token, max_age=86400)
    except BadData:
        abort(404)
    u = User.query.filter_by(email=email).first_or_404()
    login_user(u)

    return render_template("passwordreset.html", before=False, email=email, token=current_user.id)
