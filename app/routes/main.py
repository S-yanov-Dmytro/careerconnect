# app/routes/main.py

from flask import Blueprint, render_template, request, g
from app import mongo
from datetime import datetime
from flask_babel import get_locale, _

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    print("CURRENT LOCALE:", get_locale())
    page = request.args.get('page', 1, type=int)
    vacancies = list(mongo.db.vacancies.find().skip((page-1)*10).limit(10))
    now = datetime.utcnow()
    return render_template("index.html", vacancies=vacancies, now=now)

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/vacancies')
def vacancies():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    skip = (page - 1) * per_page
    vacancies = list(mongo.db.vacancies.find().skip(skip).limit(per_page))
    total = mongo.db.vacancies.count_documents({})
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total,
        'prev_num': page - 1,
        'next_num': page + 1
    }
    return render_template('vacancies.html',
                           vacancies=vacancies,
                           pagination=pagination,
                           is_new_vacancy=is_new_vacancy)

def is_new_vacancy(created_at):
    if not created_at:
        return False
    return (datetime.utcnow() - created_at).days < 7

@bp.route('/legalization')
def legalization():
    return render_template('legalization.html')

@bp.route('/faq')
def faq():
    return render_template('faq.html')

@bp.route('/cv')
def cvcreator():
    return render_template('cv.html')
