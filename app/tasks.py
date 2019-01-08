"""
celery tasks and periodic tasks of the app
"""

from flask import current_app
from celery.schedules import crontab
from datetime import date, datetime
from sqlalchemy import and_, exc
from functools import wraps

from .main import create_celery_app
from .models import db, Paper, Author, Subject, User, UserInfo, Interest, Keyword
from .analysisbackend.paperls import Paperls, kw_lst2dict
from .analysisbackend.notification import sendmail
from .conf import maildict, conf
from .cache import cache
from .security import ts
from .exceptions import appmessage

celery = create_celery_app()


def email_limit(minutes=3):  # decorator to limit the frequency of email to the same recipient
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            if cache.get(str(args) + func.__name__):
                current_app.logger.info("The email frequency is too high")
                return
            cache.set(str(args) + func.__name__, 1, 60 * minutes)
            return func(*args, **kw)

        return wrapper

    return decorator


field_list = conf['PERIODIC_FIELD_DOWNLOAD']


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=9, minute=39, day_of_week=[1, 2, 3, 4, 5]),
        arxiv_grab.s(field_list),
    )

    sender.add_periodic_task(
        crontab(hour=9, minute=49, day_of_week=[1, 2, 3, 4, 5]),
        digestion_mail.s(),
    )


@celery.task
def kwmatch_task(sdate, kw):
    ps = Paper.query.filter(Paper.announce == sdate).all()
    l = Paper.dicts(ps, kw)
    return l  # list


def paper_into_db(ps, backup=True):
    '''

    :param ps: list of dicts, papers by arxiv api, Paperls.contents
    :return: the number of items inserted
    '''
    count = 0
    if ps:
        for p in ps:
            if Paper.query.filter_by(arxivid=p['arxiv_id']).first() is None:
                prow = Paper(announce=datetime.strptime(p['announce_date'], '%Y-%m-%d').date(),
                             arxivid=p['arxiv_id'], title=p['title'],
                             summary=p['summary'], mainsubject=p['subject_abbr'][0])

                for i, a in enumerate(p['authors']):
                    prow.authors.append(Author(authorrank=i + 1, author=a))
                for i, s in enumerate(p['subject_abbr'][1:]):
                    prow.subjects.append(Subject(subject=s))

                try:
                    db.session.add(prow)
                    db.session.commit()
                    count += 1
                except exc.DataError:
                    db.session.rollback()
                    current_app.logger.warning("paper %s has illegal data to be inserted into database" % prow.arxivid)
                    if backup:
                        current_app.logger.info("try another mode to write the paper data")
                        p = Paperls(search_mode=1, id_list=[prow.arxivid])
                        counte = paper_into_db(p.contents, backup=False)
                        if counte == 0:
                            current_app.logger.error("paper %s failed to be inserted into database" % prow.arxivid)
                        elif counte == 1:
                            count += 1

    current_app.logger.info("%s papers are written into database" % count)
    return count


@celery.task
def arxiv_grab(category_list):
    current_app.logger.info("prepare to download arxiv data of today")
    lst = Paperls(search_mode=2)
    for c in category_list:
        current_app.logger.info("prepare to download arxiv data of %s" % c)
        lst.merge(Paperls(search_mode=2, search_query=c, start=2, sort_by="submittedDate"))
        paper_into_db(lst.contents)


@celery.task
def arxiv_query(search_mode=1,
                search_query="",
                id_list=[],
                start=0,
                max_results=10,
                sort_by="relevance",
                sort_order="descending"):
    ps = Paperls(search_mode, search_query, id_list, start, max_results, sort_by, sort_order)
    return paper_into_db(ps.contents)


@celery.task
def digestion_mail():
    ps = Paper.query.filter(Paper.announce == date.today()).all()
    if not ps:
        return

    # tagging is not settled here
    us = UserInfo.query.filter(and_(UserInfo.noti1 == True, UserInfo.verified == True)).all()
    for u in us:
        fs = Interest.query.filter_by(uid=u.uid).all()
        flist = [f.interest for f in fs]
        ups = [p for p in ps if p.mainsubject.startswith(tuple(flist))]
        kws = Keyword.query.filter_by(uid=u.uid).all()
        kwdict = {kw.keyword: kw.weight for kw in kws}
        lst = Paperls(search_mode=0)
        lst.contents = Paper.dicts(ups)
        lst.interest_match(kwdict)
        if lst.contents:
            user = User.query.filter_by(id=u.uid).first()
            maildict['user'] = user.email
            maildict['user_alias'] = user.name
            lst.mail(maildict)


@celery.task
@email_limit(minutes=3)
def verify_task(email, name):
    token = ts.dumps(email)
    confirm_url = current_app.config["MAIL_ABS_PATH"] + "confirm/" + token

    maildict.update({'user': email, 'user_alias': name,
                     'title': "Confirm email from myarxiv.club",
                     'content': appmessage['mail_start'] +
                                "Please use the following address to verify your account at our website.\n [ %s ]" % confirm_url})

    r = sendmail(**maildict)
    if not r[0]:
        current_app.logger.warning("the verified mail failed to sent to %s!, the error is %s" % (email, r[1].message))


@celery.task
@email_limit(minutes=2)
def reset_password_task(email, name):
    token = ts.dumps(email)
    reset_url = current_app.config["MAIL_ABS_PATH"] + "reset/" + token

    maildict.update({'user': email, 'user_alias': name,
                     'title': "Link to reset your password",
                     'content': appmessage['mail_start'] +
                                "Please use the following address to reset your password.\n [ %s ]" % reset_url})

    r = sendmail(**maildict)
    if not r[0]:
        current_app.logger.warning("the verified mail failed to sent to %s!, the error is %s" % (email, r[1].message))
