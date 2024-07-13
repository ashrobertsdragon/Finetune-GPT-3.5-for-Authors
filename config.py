import os

from decouple import config


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True

    FLASK_SECRET_KEY = config("SECRET_KEY", default="guess-me")

    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 14320

    TALISMAN_FORCE_HTTPS = True
    TALISMAN_FORCE_FILE_SAVE = True
    TALISMAN_X_XSS_PROTECTION = True
    TALISMAN_SESSION_COOKIE_SECURE = True
    TALISMAN_SESSION_COOKIE_SAMESITE = "Lax"
    TALISMAN_FRAME_OPTIONS_ALLOW_FROM = "https://www.google.com"
    TALISMAN_CSP = {
        "default-src": ["'self'"],
        "connect-src": [
            "'self'",
            "https://*.googletagmanager.com",
            "https://*.google-analytics.com",
            "https://*.analytics.google.com",
            config("SUPABASE_URL"),
            config("MAILERLITE_URL"),
        ],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "frame-src": [
            "'self'",
            "https://www.youtube.com",
            "https://connect-js.stripe.com",
            "https://js.stripe.com",
        ],
        "img-src": [
            "'self'",
            "https://*.stripe.com",
            "https://*.google-analytics.com",
            "https://*.googletagmanager.com",
        ],
        "style-src": [
            "'self'",
            "https://fonts.googleapis.com",
            "sha256-0hAheEzaMe6uXIKV4EehS9pu1am1lj/KnnzrOYqckXk=",
        ],
        "script-src": [
            "'self'",
            "https://*.googletagmanager.com",
            "https://js.stripe.com",
            "https://connect-js.stripe.com",
        ],
    }

    TALISMAN_HSTS = {"max-age": 31536000, "includeSubDomains": True}

    PROSEPAL_ENDPOINTS = {"lorebinder": "fakeendpoint"}

    def define_upload(self):
        self.UPLOAD_FOLDER = self.UPLOAD_FOLDER
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

    UPLOAD_FOLDER = os.path.join("src", "upload_folder")

    DOMAIN = config("DEV_DOMAIN")
    STRIPE_KEY = config("STRIPE_TEST_KEY", default="guess-me")
    STRIPE_PUBLISHABLE_KEY = config(
        "STRIPE_TEST_PUBLISHABLE_KEY", default="guess-me"
    )


class TestingConfig(DevelopmentConfig):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False

    UPLOAD_FOLDER = os.path.join("/tmp", "upload")

    DOMAIN = config("LIVE_DOMAIN")
    STRIPE_KEY = config("STRIPE_LIVE_KEY", default="guess-me")
    STRIPE_PUBLISHABLE_KEY = config(
        "STRIPE_LIVE_PUBLISHABLE_KEY", default="guess-me"
    )


class StagingConfig(DevelopmentConfig):
    UPLOAD_FOLDER = ProductionConfig.UPLOAD_FOLDER
