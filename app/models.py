"""
data models of the app defined by SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy
from hashlib import sha1
from flask_login import UserMixin
from .loginmanager import login_manager
from .conf import conf

db = SQLAlchemy()


class Paper(db.Model):
    __tablename__ = "paper"
    __table_args__ = {'mysql_charset': "utf8mb4"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    arxivid = db.Column(db.String(12), unique=True, nullable=False, index=True)
    title = db.Column(db.String(2048), nullable=False)
    summary = db.Column(db.TEXT, nullable=False)
    mainsubject = db.Column(db.String(32), nullable=False)
    announce = db.Column(db.Date)
    subjects = db.relationship("Subject")
    authors = db.relationship("Author")

    def __repr__(self):
        return '<Paper %r>' % self.id


class Subject(db.Model):
    __tablename__ = "subject"
    # __table_args__ = (db.UniqueConstraint('pid', 'subject', name='subject_in_paper'),
    #                   {'mysql_charset': "utf8mb4"})
    __table_args__ = {'mysql_charset': "utf8mb4"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pid = db.Column(db.Integer, db.ForeignKey("paper.id"),nullable=False)
    subject = db.Column(db.String(25),nullable=False)


class Author(db.Model):
    __tablename__ = "author"
    # __table_args__ = (db.UniqueConstraint('pid', 'author', name='author_in_paper'),
    #                   {'mysql_charset': "utf8mb4"})
    __table_args__ = {'mysql_charset': "utf8mb4"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pid = db.Column(db.Integer, db.ForeignKey("paper.id"),nullable=False)
    author = db.Column(db.String(50), nullable=False)
    authorrank = db.Column(db.Integer, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    __table_args__ = {'mysql_charset': "utf8mb4"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    # keywords = db.relationship("Keyword")
    favorites = db.relationship("Favorite")
    # interests = db.relationship("Interest")

    def dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email, "password": "******",
            "created_at": self.created_at.strftime("%Y %b %d"), "deleted": self.deleted, "admin": self.admin
        }

    def hashpass(self, salt=conf['PASSWORD_SALT']):
        pw = self.email + self.password + salt
        self.password = sha1(pw.encode('utf-8')).hexdigest()

    def checkpass(self, passtocheck, salt=conf['PASSWORD_SALT']):
        pw = self.email + passtocheck + salt
        return self.password == sha1(pw.encode('utf-8')).hexdigest()


class Keyword(db.Model):
    __tablename__ = "keyword"
    __table_args__ = {'mysql_charset': "utf8mb4"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)


class Favorite(db.Model):
    __tablename__ = "favorite"
    __table_args__ = {'mysql_charset': "utf8mb4"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey("paper.id"),nullable=False)

class UserInfo(db.Model):
    __tablename__ = "userinfo"
    __table_args__ = {'mysql_charset': "utf8mb4"}
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    noti1 = db.Column(db.Boolean, nullable=False, default=False)
    noti2 = db.Column(db.Boolean, nullable=False, default=False)
    noti3 = db.Column(db.Boolean, nullable=False, default=False)
    img = db.Column(db.String(512), nullable=False, default="")
    verified = db.Column(db.Boolean, nullable=False, default=False)
    profile = db.Column(db.TEXT, nullable=False, default="")

    def dict(self):
        return {"uid": self.uid, "dailymail": self.noti1, "img": self.img,
                "verified": self.verified, "profile": self.profile}

class Interest(db.Model):
    __tablename__ = "interest"
    __table_args__ = {'mysql_charset': "utf8mb4"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    interest = db.Column(db.String(50), nullable=False)