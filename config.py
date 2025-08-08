import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = 'SECRET_KEY'
    if not SECRET_KEY:
        raise RuntimeError('SECRET_KEY must be set in environment variables')
    MONGO_URI = 'mongodb+srv://donkarte:01986774@users.4ifyufj.mongodb.net/site_for_roma?retryWrites=true&w=majority&appName=Users'
    if not MONGO_URI:
        raise RuntimeError('MONGO_URI must be set in environment variables')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    RATELIMIT_DEFAULT = "100 per day"
    RATELIMIT_STORAGE_URL = "memory://"

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
