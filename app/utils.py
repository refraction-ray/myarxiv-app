import re
from hashlib import sha1, md5
from datetime import datetime

from .analysisbackend.cons import category
from .conf import conf
from .security import tscf


def get_arxiv_url(paper):
    if len(paper.arxivid.split(".")) == 1:
        url = "https://arxiv.org/abs/" + paper.mainsubject + "/" + paper.arxivid
    else:
        url = "https://arxiv.org/abs/" + paper.arxivid
    return url


def get_pdf_url(arxiv_url):
    pdf_url = re.subn("abs", "pdf", arxiv_url)[0]
    return pdf_url + ".pdf"


def get_subject_url(subject):
    return "https://arxiv.org/list/" + subject + "/recent"


def recover_subject(subject_abbr):
    try:
        s = category[subject_abbr]
        return s
    except KeyError:
        pass


def ctokenize(uid):  # can be registered as jinja filters
    return tscf.dumps(uid)


def get_gravatar_url(email):
    gravatar_url = "https://www.gravatar.com/avatar/" + md5(email.lower().encode('utf8')).hexdigest()
    return gravatar_url + "?d=" + conf["GRAVATA_IMAGE_DEFAULT"]


def hashpass(user, pw, salt):
    pw = user + pw + salt
    return sha1(pw.encode('utf-8')).hexdigest()


def str2list(s, minl=3):  # make comma separated string as list
    return [r.strip() for r in list(s.split(",")) if len(r.strip()) > minl]


def timeoutseconds():
    now = datetime.now()
    print("time now is %s" % now)
    update = datetime(year=now.year, month=now.month, day=now.day, hour=9, minute=50)
    s = (update - now).total_seconds()
    if s > 0:
        return int(s)
    else:
        return int(86400 - s)


class get_page:
    def __init__(self, l, page, nums=10):
        self.list = l
        self.page = page
        self.nums = nums
        self.contents()

    def contents(self):
        start = (self.page - 1) * self.nums
        end = self.page * self.nums
        le = len(self.list)
        self.first = 1
        self.last = int((le - 1) / self.nums) + 1
        if le >= end:
            self.items = self.list[start:end]
            if le == end:
                self.has_next = False
            else:
                self.has_next = True
            if self.page > 1:
                self.has_prev = True
            else:
                self.has_prev = False

        elif le >= start:
            self.items = self.list[start:]
            self.has_next = False
            if self.page > 1:
                self.has_prev = True
            else:
                self.has_prev = False
        else:
            self.items = []
            self.has_next = False
            self.has_prev = False

    def __repr__(self):
        return {"has_next": self.has_next,
                "has_prev": self.has_prev,
                "first": self.first,
                "last": self.last,
                "items": self.items,
                "page": self.page,
                "nums": self.nums
                }

    __str__ = __repr__

    dict = __repr__


def pagetodict(pgobj):  # pageobj defined in flask_sqlalchemy, make the interface consitent with customized getpage
    return {"has_prev": pgobj.has_prev,
            "has_next": pgobj.has_next, "prev_num": pgobj.prev_num,
            "next_num": pgobj.next_num, "page": pgobj.page, "nums": pgobj.per_page,
            "last": pgobj.pages}
