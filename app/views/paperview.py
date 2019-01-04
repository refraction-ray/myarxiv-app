from flask import (Blueprint, request, jsonify, url_for, current_app,
                   render_template, abort, redirect)
from ..models import Paper
from ..exceptions import *
from ..utils import get_arxiv_url, get_pdf_url
from flask_login import login_required, current_user
from ..tasks import arxiv_query

paperview = Blueprint('paperview', __name__)


@paperview.route('/')
def index():
    keyword = request.args.get('keyword', "")
    date = request.args.get('date', "")
    page = request.args.get('page', "") or "1"
    return render_template("paperlist.html", date=date, page=page, favlist=False)


@paperview.route('/paper/<arxivid>')
def paperbyid(arxivid):
    p = Paper.query.filter_by(arxivid=arxivid).first()
    if not p:
        fetchtask = arxiv_query.delay(search_mode=1, id_list=[arxivid])
        return render_template("comingsoon.html", tid=fetchtask.id)
    p.arxivurl = get_arxiv_url(p)
    p.pdfurl = get_pdf_url(p.arxivurl)
    return render_template("paperitem.html", p=p)


@paperview.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', "") or "1"
    return render_template("paperlist.html", page=page, favlist=True)
