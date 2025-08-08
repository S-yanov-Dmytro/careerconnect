from flask import Flask, request, g
from flask_babel import Babel

SUPPORTED_LANGUAGES = ['ru', 'pl', 'uk', 'en']

def get_locale():
    lang = request.args.get('lang_code')
    if lang in SUPPORTED_LANGUAGES:
        return lang
    browser_lang = request.accept_languages.best_match(SUPPORTED_LANGUAGES)
    if browser_lang:
        return browser_lang
    return 'ru'

def create_app():
    app = Flask(__name__)
    app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
    babel = Babel(app, locale_selector=get_locale)

    @app.before_request
    def before_request():
        g.lang_code = get_locale()
        print(f"🌍 Current locale: {g.lang_code}")

    @app.route('/')
    def index():
        # Тестовий фіксований текст без перекладу
        return f"<h1>Привіт, світ!</h1><p>Поточна мова (locale): {g.lang_code}</p>"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
