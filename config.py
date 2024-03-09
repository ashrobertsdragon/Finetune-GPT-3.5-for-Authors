import os
from decouple import config

DATABASE_URI = config("DATABASE_URL")
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    FLASK_SECRET_KEY = config("SECRET_KEY", default="guess-me")
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = True
    UPLOAD_FOLDER = os.path.join("src", "upload_folder")


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    DEBUG_TB_ENABLED = False
    UPLOAD_FOLDER = os.path.join("/tmp", "upload")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class StagingConfig(ProductionConfig):
    DEBUG = True
    DEBUG_TB_ENABLED = True
    WTF_CSRF_ENABLED = False
    