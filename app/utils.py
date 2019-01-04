import re
from hashlib import sha1, md5
from datetime import datetime
from .analysisbackend.cons import category
from .analysisbackend.paperls import Paperls
from .conf import conf
from .security import ts


def jsonfrom(ps):
    l = []
    for p in ps:
        m = {}
        m['pid'] = p.id
        m['arxiv_id'] = p.arxivid
        m['title'] = p.title
        m['summary'] = p.summary
        m['subject_abbr'] = [p.mainsubject]
        m['subject_abbr'].extend([s.subject for s in p.subjects])
        authorwithrank = sorted([(a.authorrank, a.author) for a in p.authors], key=lambda x: x[0])
        m['authors'] = [a[1] for a in authorwithrank]
        m['date'] = p.announce.strftime("%Y-%m-%d")
        m['arxiv_url'] = get_arxiv_url(p)
        m['favorite'] = 0
        l.append(m)
    return l


def jsonwithkw(json, kwdict):
    lst = Paperls(search_mode=0)
    lst.contents = json
    lst.interest_match(kwdict)
    # res = [p for p in lst.contents if p.get('keyword', None)]
    res = sorted([c for c in lst.contents if c.get('keyword', None)], key=lambda s: s['weight'], reverse=True)
    return res


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
    return ts.dumps(uid)


def get_gravatar_url(email):
    gravatar_url = "https://www.gravatar.com/avatar/" + md5(email.lower().encode('utf8')).hexdigest()
    return gravatar_url + "?d=" + conf["GRAVATA_IMAGE_DEFAULT"]


def hashpass(user, pw, salt):
    pw = user + pw + salt
    return sha1(pw.encode('utf-8')).hexdigest()


def generate_backend_pass(user, pw, salt):
    pw = sha1(pw.endcoe('utf-8')).hexdigest()
    return hashpass(user, pw, salt)


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


def pagetodict(pgobj):  # pageobj defined in flask_sqlalchemy
    return {"has_prev": pgobj.has_prev,
            "has_next": pgobj.has_next, "prev_num": pgobj.prev_num,
            "next_num": pgobj.next_num, "page": pgobj.page, "nums": pgobj.per_page,
            "last": pgobj.pages}
