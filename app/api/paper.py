from flask import Blueprint, request, jsonify, url_for, current_app
from datetime import date, datetime, timedelta
import json
from flask_login import current_user, login_required
from sqlalchemy import and_, or_

from ..models import db, Paper, Keyword, Favorite, Interest
from ..tasks import kwmatch_task, arxiv_query
from ..utils import get_page, pagetodict, timeoutseconds, str2list
from ..cache import cache
from ..exceptions import InvalidInput

paper = Blueprint('paper', __name__)


@paper.route('/api/today')  # only support data param and page param
def api_today():
    todaystring = date.today().strftime("%Y%m%d")
    dtstring = request.args.get("date", todaystring) or todaystring  # only support one day, similar to new in arxiv
    # the recent API is separated and to be implemented
    pgstring = request.args.get("page", "1") or "1"
    try:
        pg = int(pgstring)
    except ValueError:
        pg = 1
    try:
        dt = datetime.strptime(dtstring, "%Y%m%d").date()
    except ValueError:
        dtstring = todaystring
        dt = date.today()
    cachekey = "api_today_" + str(getattr(current_user, "id", "")) + dtstring
    current_app.logger.info("find cache key on %s" % cachekey)
    res = cache.get(cachekey)
    if res is not None:
        current_app.logger.info("using cache")
        return jsonify({"results": get_page(res, pg).dict()})

    if not current_user.is_authenticated:
        ps = Paper.query.filter(Paper.announce == dt).paginate(1, 200,
                                                               False).items  # limit the recourse for unregistered user
        prev = 0
        while not ps:
            dt -= timedelta(days=1)
            ps = Paper.query.filter(Paper.announce == dt).paginate(1, 200, False).items
            prev += 1
            if prev > 3:
                break
        jsonrs = Paper.dicts(ps)
        res = jsonify({"results": get_page(jsonrs, pg).dict()})

        current_app.logger.info("set cache key as %s" % cachekey)
        cache.set(cachekey, jsonrs, timeout=3600 * 6)
        return res

    # if logged in
    fs = Interest.query.filter_by(uid=current_user.id).all()
    flist = [f.interest for f in fs]
    ps = Paper.query.filter(Paper.announce == dt).all()
    prev = 0
    while not ps:
        dt -= timedelta(days=1)
        ps = Paper.query.filter(Paper.announce == dt).all()
        prev += 1
        if prev > 5:
            break
    ps = [p for p in ps if p.mainsubject.startswith(tuple(flist))]

    kws = Keyword.query.filter_by(uid=current_user.id).all()
    kw_dict = {kw.keyword: kw.weight for kw in kws}
    l = Paper.dicts(ps, kw_dict)
    res = jsonify({"results": get_page(l, pg).dict()})

    current_app.logger.info("set cache key as %s" % cachekey)
    cache.set(cachekey, l, timeout=timeoutseconds())
    return res


@paper.route('/api/favorites', methods=["GET", "POST"])
@login_required
def api_favorites():
    if request.method == "POST":
        try:
            paperid = request.json.get('id', [])
        except AttributeError:
            raise InvalidInput("illegal form of post body")
        fs = Favorite.query.filter(and_(Favorite.uid == current_user.id, Favorite.pid.in_(paperid))).all()
        fsid = set([f.pid for f in fs])
        r = []
        for pid in paperid:
            if pid in fsid:
                r.append(1)
            else:
                r.append(0)
        res = jsonify({'results': r})
        return res

    # GET method, fetch all favorites paper in json form
    pg = int(request.args.get("page", "1") or "1")
    fs = Favorite.query.filter(Favorite.uid == current_user.id).paginate(pg, 10, False)
    pid = [f.pid for f in fs.items]
    ps = Paper.query.filter(Paper.id.in_(pid)).all()

    res = {"items": Paper.dicts(ps)}
    res.update(pagetodict(fs))
    return jsonify({"results": res})


@paper.route('/api/favorites/add', methods=["POST"])
@login_required
def api_favorites_add():
    paperid = request.json.get('id', [])
    for pid in paperid:
        if not Favorite.query.filter(and_(Favorite.uid == current_user.id, Favorite.pid == pid)).all():
            db.session.add(Favorite(uid=current_user.id, pid=pid))
    db.session.commit()
    return jsonify({"message": "the papers are added to your favorites successfully"})


@paper.route('/api/favorites/switch', methods=["POST"])
@login_required
def api_favorites_switch():
    paperid = request.json.get('id', [])
    for pid in paperid:
        f = Favorite.query.filter(and_(Favorite.uid == current_user.id, Favorite.pid == pid)).first()
        if not f:
            db.session.add(Favorite(uid=current_user.id, pid=pid))
        else:
            db.session.delete(f)
    db.session.commit()
    return jsonify({"message": "the papers are switched in terms of favorites"})


@paper.route('/api/query', methods=['POST'])
def api_query():
    """
    implemented options include:
    authors(list, full name is required), dates (list, in the form %Y-%m-%d)
    subjects (list), page(int), limit(int, how many items in one page), keywords(list),
    default_keywords (bool, add keywords of the user in the search list)
    default_subjects (bool), favorites(bool, only include favorite paper of the user)
    for authors, keywords and subjects, comma separated string is also supported
    :return:
    """
    r = request.json
    cache_key = json.dumps(r) + str(getattr(current_user, "id", ""))
    c = cache.get(cache_key)

    try:
        page = r.get('page', None) or request.args.get('page', None) or "1"
        page = int(page)
        limit = r.get('limit', "10")
        limit = int(limit)
        if limit > 100:
            limit = 100
    except (TypeError, ValueError) as e:
        raise InvalidInput(message="invalid form of pages")

    if c:
        return jsonify({"results": get_page(c, page, nums=limit).dict()})

    dates = r.get('dates', []) or []
    if not dates:
        dates = []
        for d in range(30):
            dates.append((date.today() - timedelta(days=d)).strftime("%Y-%m-%d"))

    try:
        if isinstance(dates, dict):
            ds = datetime.strptime(dates.get('start'), "%Y-%m-%d").date()
            de = datetime.strptime(dates.get('end'), "%Y-%m-%d").date()
            dates = [ds + timedelta(days=x) for x in range((de - ds).days + 1)][:180]
        else:
            dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in dates[:180]]
    except (TypeError, ValueError) as e:
        raise InvalidInput(message="invalid form of date strings")

    if not current_user.is_authenticated:
        dates = dates[:60]

    subjects = r.get('subjects', []) or []
    if isinstance(subjects, str):
        subjects = str2list(subjects)
    default_subjects = r.get('default_subjects', False)
    try:
        if default_subjects and current_user.is_authenticated:
            ss = Interest.query.filter_by(uid=current_user.id).all()
            ss_subject = [s.interest for s in ss]
            subjects.extend(ss_subject)
        subjects = list(subjects)
    except (TypeError, ValueError) as e:
        raise InvalidInput(message="invalid form of subjects")

    if subjects:
        ps = Paper.query.filter(and_(Paper.announce.in_(dates), or_(
            *[Paper.mainsubject.like(start + "%") for start in subjects]
        ))).all()
    else:
        ps = Paper.query.filter(Paper.announce.in_(dates)).all()

    favorite = r.get('favorites', False)
    if favorite and current_user.is_authenticated:
        fs = Favorite.query.filter_by(uid=current_user.id).all()
        fs_set = set([f.pid for f in fs])
        ps = [p for p in ps if p.id in fs_set]

    authors = r.get('authors', None)
    if isinstance(authors, str):
        authors = str2list(authors)
    if authors:
        try:
            authors = set(authors)
            ps = [p for p in ps if authors.intersection(set([a.author for a in p.authors]))]
        except (TypeError, ValueError) as e:
            raise InvalidInput(message="invalid form of authors")

    keywords = r.get('keywords', []) or []
    if isinstance(keywords, str):
        keywords = str2list(keywords)
    default_keywords = r.get('default_keywords', False)
    try:
        if default_keywords and current_user.is_authenticated:
            ks = Keyword.query.filter_by(uid=current_user.id).all()
            keywords.extend([k.keyword for k in ks])
        kw_dict = {k: 1 for k in keywords}
    except (TypeError, ValueError) as e:
        raise InvalidInput(message="invalid form of keywords")

    if not kw_dict:
        kw_dict = None
    jsonrs = Paper.dicts(ps, kw_dict)

    jsonrs = sorted(jsonrs, key=lambda x: x['date'], reverse=True)  # maybe add sorted keys option later

    if len(jsonrs) > 300:
        timeout = 60 * 10
    else:
        timeout = 60 * 60
    cache.set(cache_key, jsonrs, timeout)

    return jsonify({"results": get_page(jsonrs, page, nums=limit).dict()})

"""
@paper.route('/api/papers', methods=["POST"])
def paperbyid():
    paperid = request.json.get('id', [])
    ps = Paper.query.filter(Paper.arxivid.in_(paperid)).all()
    return jsonify(Paper.dicts(ps))
"""

@paper.route('/api/kwmatch/result/<task_id>')
def paperbykw_result(task_id):
    current_app.logger.info("begin query the status of the result")
    fetch_task = kwmatch_task.AsyncResult(task_id)
    current_app.logger.info("the result status is %s" % fetch_task.ready())
    if fetch_task.ready() is False:
        response = {
            'state': str(fetch_task.status),
            'msg': "not finished yet"
        }
    else:
        response = fetch_task.get()
    return jsonify(response)


@paper.route('/api/kwmatch', methods=["POST"])
def paperbykw():
    sdate = request.json.get('date', None)
    if sdate is None:
        sdate = date.today()
    else:
        sdate = datetime.strptime(sdate, "%Y-%m-%d")
    kw = request.json.get('keywords', None)

    match_task = kwmatch_task.delay(sdate, kw)

    return jsonify(), 202, \
           {'Location': url_for('paper.paperbykw_result',
                                task_id=match_task.id)}


@paper.route('/api/download', methods=["POST"])
def downloadpaper():
    query_task = arxiv_query.delay(**request.json)

    return jsonify({"status": "accepted"})


@paper.route('/api/status/<taskid>')
def valid_paper(taskid):
    task = arxiv_query.AsyncResult(taskid)
    if task.ready() is False:
        response = {
            'state': -1
        }
    else:
        response = {'state': task.get()}
    return jsonify(response)


@paper.route('/api/test', methods=['GET', 'POST'])
def api_test():
    # # list of form data
    # r = request.form.getlist("a")
    # return jsonify({"a": r})
    # # process_data of wtforms
    # form = QueryForm(**request.json)
    # return jsonify(form.data )
    pass
