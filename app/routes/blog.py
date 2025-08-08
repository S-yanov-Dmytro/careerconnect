from flask import Blueprint, render_template, current_app
from app import mongo
from app.models.post import Post
from datetime import datetime
from bson.objectid import ObjectId
from flask_babel import format_datetime
from flask import g

bp = Blueprint('blog', __name__, url_prefix='/blog')

def estimate_read_time(content):
    words_per_minute = 200
    word_count = len(content.split())
    return max(1, round(word_count / words_per_minute))

from flask import g
def format_date_locale(date, lang):
    months = {
        'ru': {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        },
        'ua': {
            1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня',
            5: 'травня', 6: 'червня', 7: 'липня', 8: 'серпня',
            9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'
        },
        'pl': {
            1: 'stycznia', 2: 'lutego', 3: 'marca', 4: 'kwietnia',
            5: 'maja', 6: 'czerwca', 7: 'lipca', 8: 'sierpnia',
            9: 'września', 10: 'października', 11: 'listopada', 12: 'grudnia'
        },
        'en': {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        },
        'de': {
            1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
            5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
        }
    }
    month = months.get(lang, months['ru'])[date.month]
    return f"{date.day} {month} {date.year}"

@bp.route('/')
def index():
    posts = Post.get_all_posts(mongo)
    for post in posts:
        post['read_time'] = estimate_read_time(post.get('content', ''))
        post['formatted_date'] = format_datetime(post['created_at'], "d MMMM yyyy")
        post['id'] = str(post['_id'])
        post['views'] = post.get('views', 0)
    return render_template('blog.html', posts=posts)

@bp.route('/<post_id>')
def view_post(post_id):
    try:
        mongo.db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$inc': {'views': 1}}
        )

        post = Post.get_post(mongo, post_id)
        if post:
            post['read_time'] = estimate_read_time(post.get('content', ''))
            post['formatted_date'] = format_date_locale(post['created_at'], g.lang_code)
            post['views'] = post.get('views', 0)
            return render_template('post.html', post=post)
    except Exception as e:
        current_app.logger.error(f"Error viewing post {post_id}: {str(e)}")
    return render_template('404.html'), 404
