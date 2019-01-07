from flask import Blueprint, request, redirect, url_for, current_app, abort, jsonify
from ..models import db, User, Keyword, UserInfo, Interest
from ..exceptions import *
from ..forms import RegistrationForm, LoginForm, UserInfoForm, EmailForm
from datetime import datetime
from flask_login import login_required, login_user, current_user, logout_user
from ..cache import cache
from ..utils import get_gravatar_url
from ..tasks import verify_task, reset_password_task
from ..security import token_checked
from ..analysisbackend.cons import field

user = Blueprint('user', __name__)


@user.route("/api/registration", methods=["POST"])
def api_registration():
    current_app.logger.info("get request for registration %s" % request.form)
    form = RegistrationForm(request.form)
    if not form.validate():
        raise InvalidInput(message="Incorrect input in the form", payload=form.errors)
    if User.query.filter_by(email=form.email.data).first() is not None:
        raise InvalidInput(message="The email address has already been used.")
    if User.query.filter_by(name=form.name.data).first() is not None:
        raise InvalidInput(message="The username has already been used.")
    u = User(name=form.name.data, email=form.email.data, password=form.password.data, created_at=datetime.now())
    u.hashpass()
    if u.id == 1:
        u.admin = True
    db.session.add(u)
    db.session.commit()
    ui = UserInfo(uid=u.id, img=get_gravatar_url(u.email))
    db.session.add(ui)
    db.session.commit()
    return jsonify({'message': 'the user is successfully created',
                    'state': 'success'})


@user.route("/api/login", methods=["POST"])
def api_login():
    current_app.logger.info("get request for login %s" % request.form)
    form = LoginForm(request.form)
    current_app.logger.info("email %s, password %s***" % (form.email.data, form.password.data[:2]))
    # u = User.query.filter_by(email=form.email.data).first()
    u = User.get(email=form.email.data)
    if not form.validate():
        raise InvalidInput(message="Incorrect input in the form", payload=form.errors)
    if not u:
        raise InvalidInput(message="The password or email is in correct")

    tries = cache.get("uid_login" + u.email)
    if tries:
        if tries > 5:
            current_app.logger.info("exceed the max tried of wrong login for user %s" % u.id)
            raise InvalidInput(message="Please wait for 5 minutes to try again")
    else:
        tries = 0

    if u.checkpass(form.password.data, current_app.config['PASSWORD_SALT']):
        current_app.logger.info("successfully login!")
        login_user(u)
        return jsonify({'message': "successfully login",
                        'state': 'success'})

    current_app.logger.info("count the tries of invalid password: %s times" % (tries + 1))
    cache.set("uid_login" + u.email, tries + 1, 5 * 60)
    raise InvalidInput(message="The password or email is incorrect")


@user.route("/api/logout")
# @login_required
def api_logout():  # weird combination between view and api?
    logout_user()
    return jsonify({'state': 'success',
                    'message': "successfully log out"})


@user.route("/api/keywords", methods=["GET", "POST"])
@login_required
@token_checked
def api_keywords():
    if request.method == "GET":
        ks = Keyword.query.filter_by(uid=current_user.id).all()
        ks = [{"keyword": k.keyword, "weight": k.weight} for k in ks]
        return jsonify({"results": ks})
    else:
        js = request.json['items']
        u = current_user
        try:
            u.keywords = [Keyword(keyword=j['keyword'][:90], weight=j['weight']) for j in js if
                       len(j.get('keyword', "")) > 0]
            u.save()
        except (KeyError, ValueError) as e:
            raise InvalidInput(message="Something went wrong in the keyword form")
        # try delete relevant cache as much as possible
        cache.delete("api_today_" + str(current_user.id) + datetime.today().strftime("%Y%m%d"))
        return jsonify({"message": "the keywords are successfully updated",
                        'state': 'success'})


@user.route("/api/fields", methods=["GET", "POST"])
@login_required
@token_checked
def api_fields():
    if request.method == "GET":
        fs = Interest.query.filter_by(uid=current_user.id).all()
        fs_set = {f.interest for f in fs}
        field_dict = {f: f in fs_set for f in field}
        return jsonify(field_dict)
    ## post part
    js = request.json['fields']
    u = current_user
    try:
        u.interests = [Interest(interest=j['abbr'][:45]) for j in js if j.get('checked', False) is True]
        u.save()
    except (KeyError, ValueError) as e:
        raise InvalidInput(message="Something went wrong in the interest field form")

    return jsonify({"message": "the interest fields are successfully updated",
                    'state': 'success'})


@user.route("/api/userinfo", methods=["GET", "POST"])
@login_required
@token_checked
def api_userinfo():
    if request.method == "GET":
        ui = UserInfo.query.filter_by(uid=current_user.id).first()
        u = User.query.filter_by(id=current_user.id).first()
        if not ui:
            ui = UserInfo(uid=current_user.id, img=get_gravatar_url(u.email))
            db.session.add(ui)
            db.session.commit()
        res = u.dict()
        res.update(ui.dict())
        return jsonify(res)

    ## method post
    ui = UserInfo.query.filter_by(uid=current_user.id).first()
    form = UserInfoForm(request.form)
    if not form.validate():
        raise InvalidInput(message="Incorrect input in the form", payload=form.errors)
    ui.img = form.imgurl.data
    ui.profile = form.profile.data
    if ui.verified:
        ui.noti1 = form.dailymail.data
    db.session.commit()
    return jsonify({"state": "success",
                    "message": "the user info is successfully updated"})


@user.route("/api/verify")  # better implement in post
@login_required
def api_verify():
    u = User.query.filter_by(id=current_user.id).first()
    task = verify_task.delay(u.email, u.name)
    current_app.logger.info("Sending verification email for %s" % u.name)
    return jsonify({"state": "sending",
                    "message": "An verification mail is sent to you, please click the link inside the mail to verify.\n" +
                               appmessage['mail_check']})


@user.route("/api/password/reset", methods=["POST"])
def api_password_reset():
    form = EmailForm(request.form)
    if not form.validate():
        raise InvalidInput(message="Incorrect input in the form", payload=form.errors)
    u = User.query.filter_by(email=form.email.data).first()
    if not u:
        raise InvalidInput(message="No user use this email address")
    ui = UserInfo.query.filter_by(uid=u.id).first()
    if (not ui) or (not getattr(ui, "verified", False)):
        raise InvalidInput(message="The email isn't verified, so you cannot reset the password")
    task = reset_password_task.delay(u.email, u.name)
    current_app.logger.info("Sending reset email for %s" % u.name)
    return jsonify({"state": "sending",
                    "message": "A reset mail is sent to you, please click the link inside to reset the password.\n" +
                               appmessage['mail_check']})


@user.route("/api/password/edit", methods=["POST"])
@login_required
@token_checked
def api_password_edit():
    current_app.logger.info(request.form)
    password = request.form.get("password")
    email = request.form.get("email")
    u = User.query.filter_by(email=email).first()
    if not u:
        raise InvalidInput(message="Don't try to do something weird")
    ui = UserInfo.query.filter_by(uid=u.id).first()
    if (not ui) or (not getattr(ui, "verified", False)):
        raise InvalidInput(message="Don't try to do something weird")
    u.password = password
    u.hashpass(current_app.config['PASSWORD_SALT'])
    db.session.commit()
    return jsonify({"message": "the password is successfully changed",
                    'state': 'success'})
