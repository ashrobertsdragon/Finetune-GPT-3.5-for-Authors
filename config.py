import os
from decouple import config


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    FLASK_SECRET_KEY = config("SECRET_KEY", default="guess-me")
    WTF_CSRF_ENABLED = True

    def define_upload(self):
        self.UPLOAD_FOLDER = self.UPLOAD_FOLDER
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join("src", "upload_folder")
    STRIPE_KEY = config("STRIPE_TEST_KEY", default="guess-me")
    STRIPE_PUBLISHABLE_KEY = config("STRIPE_TEST_PUBLISHABLE_KEY", default="guess-me")


class TestingConfig(DevelopmentConfig):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    STRIPE_KEY = config("STRIPE_LIVE_KEY", default="guess-me")
    STRIPE_PUBLISHABLE_KEY = config("STRIPE_LIVE_PUBLISHABLE_KEY", default="guess-me")
    UPLOAD_FOLDER = os.path.join("/tmp", "upload")


class StagingConfig(DevelopmentConfig):
    UPLOAD_FOLDER = ProductionConfig.UPLOAD_FOLDER
