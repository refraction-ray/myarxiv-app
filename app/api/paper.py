from flask import Blueprint, request, jsonify, url_for, current_app
from datetime import date, datetime, timedelta
from ..models import db, Paper, Keyword, Favorite, Interest
from ..tasks import kwmatch_task, arxiv_query
from ..utils import jsonfrom, jsonwithkw, get_page, pagetodict, timeoutseconds
from flask_login import current_user, login_required
from sqlalchemy import and_
from ..cache import cache

paper = Blueprint('paper', __name__)


@paper.route('/api/today')
def api_today():
    todaystring = date.today().strftime("%Y%m%d")
    dtstring = request.args.get("date", todaystring) or todaystring # only support one day, similar to new in arxiv
                                                                    # the recent API is separated and to be implemented
    kwstring = request.args.get("keyword", "") # support multi keywords separated by ,
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
    cachekey = "api_today_" + str(getattr(current_user, "id", "")) + dtstring + kwstring
    current_app.logger.info("find cache key on %s" % cachekey)
    res = cache.get(cachekey)
    if res is not None:
        current_app.logger.info("using cache")
        return jsonify({"results": get_page(res, pg).dict()})

    if not current_user.is_authenticated:
        ps = Paper.query.filter(Paper.announce == dt).paginate(1, 100,
                                                               False).items  # limit the recourse for unregistered user
        prev = 0
        while not ps:
            dt -= timedelta(days=1)
            ps = Paper.query.filter(Paper.announce == dt).paginate(1, 100, False).items
            prev += 1
            if prev > 3:
                break
        jsonrs = jsonfrom(ps)
        if not kwstring:
            res = jsonify({"results": get_page(jsonrs, pg).dict()})
        else:
            kwstrings = kwstring.split(",")
            jsonrs = jsonwithkw(jsonrs, {kw: 1 for kw in kwstrings})
            res = jsonify({"results": get_page(jsonrs, pg).dict()})
        cachekey = "api_today_" + dtstring + kwstring
        current_app.logger.info("set cache key as %s" % cachekey)
        cache.set(cachekey, jsonrs, timeout=3600)
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
    jsonrs = jsonfrom(ps)
    if not kwstring:
        kws = Keyword.query.filter_by(uid=current_user.id).all()
        kw_dict = {kw.keyword: kw.weight for kw in kws}
    else:
        kwstrings = kwstring.split(",")
        kw_dict = {kw: 1 for kw in kwstrings}
    l = jsonwithkw(jsonrs, kw_dict)
    res = jsonify({"results": get_page(l, pg).dict()})
    cachekey = "api_today_" + str(current_user.id) + dtstring + kwstring
    current_app.logger.info("set cache key as %s" % cachekey)
    cache.set(cachekey, l, timeout=timeoutseconds())
    return res


@paper.route('/api/favorites', methods=["GET", "POST"])
@login_required
def api_favorites():
    if request.method == "POST":
        paperid = request.json.get('id', [])
        # current_app.logger.info("the paperid are %s"%str(paperid))
        fs = Favorite.query.filter(and_(Favorite.uid == current_user.id, Favorite.pid.in_(paperid))).all()
        fsid = [f.pid for f in fs]
        r = []
        for pid in paperid:
            if pid in fsid:
                r.append(1)
            else:
                r.append(0)
        res = jsonify({'results': r})
        return res
    # GET method, fetch all favorites paper json
    pg = int(request.args.get("page", "1") or "1")
    fs = Favorite.query.filter(Favorite.uid == current_user.id).paginate(pg, 10, False)
    pid = [f.pid for f in fs.items]
    ps = Paper.query.filter(Paper.id.in_(pid)).all()
    l = jsonfrom(ps)
    res = {"items": l}
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


@paper.route('/api/papers', methods=["POST"])
def paperbyid():
    paperid = request.json.get('id', [])
    ps = Paper.query.filter(Paper.arxivid.in_(paperid)).all()
    l = jsonfrom(ps)
    return jsonify(l)


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
