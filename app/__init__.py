from flask import Flask, request, g, session
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel, gettext
import os
translations_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'translations'))

from app.models.user import User  # Імпорт твоєї моделі User


mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache(config={'CACHE_TYPE': 'simple'})
limiter = Limiter(key_func=get_remote_address)
babel = Babel()

SUPPORTED_LANGUAGES = ['ru', 'pl', 'en']

@login_manager.user_loader
def load_user(user_id):
    # Шукає користувача в базі по id (MongoDB)
    return User.get_user(mongo, user_id)

def get_locale():
    # 1. Якщо в URL передано lang_code — зберегти в сесію
    lang = request.args.get('lang_code')
    if lang in SUPPORTED_LANGUAGES:
        session['lang'] = lang  # ← Зберігаємо в сесію
        return lang

    # 2. Якщо вже вибрано в сесії
    if 'lang' in session:
        return session['lang']

    # 3. Вибір за мовою браузера
    browser_lang = request.accept_languages.best_match(SUPPORTED_LANGUAGES)
    if browser_lang:
        print(f"Choose by browser: {browser_lang}")
        return browser_lang

    # 4. Дефолт
    return 'ru'


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    babel.init_app(
        app,
        locale_selector=get_locale,
        default_translation_directories=translations_path,
        default_domain="messages",
        default_locale="ru"

    )


    @app.before_request
    def detect_lang():
        g.lang_code = get_locale()

    @app.context_processor
    def inject_globals():
        return {
            'lang_code': g.lang_code,
            '_': gettext,
            'gettext': gettext
        }

    from app.routes import blog, admin, main, auth
    app.register_blueprint(blog.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
