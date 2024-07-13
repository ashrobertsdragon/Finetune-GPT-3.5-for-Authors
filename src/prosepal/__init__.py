# Config classes for environment variables
from config import (
    DevelopmentConfig,
    ProductionConfig,
    StagingConfig,
    TestingConfig
)
from decouple import config
from flask import Flask
from flask_session import Session
from flask_talisman import Talisman
from loguru import logger
# Import blueprints
from prosepal.accounts.views import accounts_app
from prosepal.binders.views import binders_app
from prosepal.core.views import core_app
from prosepal.free.views import free_app
from prosepal.mailerlite.views import mailerlite_app
from prosepal.stripe.views import stripe_app

from .cache import cache
from .utils import inject_user_context, load_user

app = Flask(__name__)

env_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}

# Load environment variable for flask environment configuration class
config_name = config("FLASK_ENV", default="development")
app.config.from_object(env_config[config_name])

app.secret_key = config("FLASK_SECRET_KEY")


app.logger.debug = logger.debug
app.logger.info = logger.info
app.logger.warning = logger.warning
app.logger.error = logger.error
app.logger.critical = logger.critical
app.logger.exception = logger.exception


@app.before_request
def before_each_request():
    load_user()


app.context_processor(inject_user_context)

# Register Blueprints
app.register_blueprint(accounts_app)
app.register_blueprint(binders_app)
app.register_blueprint(core_app)
app.register_blueprint(free_app)
app.register_blueprint(stripe_app)
app.register_blueprint(mailerlite_app)


Session(app)
cache.init_app(
    app,
    config={
        "CACHE_TYPE": app.config["CACHE_TYPE"],
        "CACHE_DEFAULT_TIMEOUT": app.config["CACHE_DEFAULT_TIMEOUT"],
    },
)

Talisman(
    app,
    force_https=app.config["TALISMAN_FORCE_HTTPS"],
    force_file_save=app.config["TALISMAN_FORCE_FILE_SAVE"],
    session_cookie_secure=app.config["TALISMAN_SESSION_COOKIE_SECURE"],
    session_cookie_samesite=app.config["TALISMAN_SESSION_COOKIE_SAMESITE"],
    frame_options_allow_from=app.config["TALISMAN_FRAME_OPTIONS_ALLOW_FROM"],
    content_security_policy=app.config["TALISMAN_CSP"],
    strict_transport_security=app.config["TALISMAN_HSTS"],
)
