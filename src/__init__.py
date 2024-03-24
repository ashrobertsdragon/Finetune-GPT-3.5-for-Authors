from decouple import config
from flask import Flask
from flask_session import Session

# Config classes for environment variables
from config import DevelopmentConfig, TestingConfig, StagingConfig, ProductionConfig

from .utils import load_user, inject_user_context
# Import blueprints
from src.accounts.views import accounts_app
from src.binders.views import binders_app
from src.core.views import core_app
from src.free.views import free_app
from src.stripe.views import stripe_app

app = Flask(__name__)

env_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig
}

# Load environment variable for flask environment configuration class
config_name = config("FLASK_ENV", default="development")
app.config.from_object(env_config[config_name])

app.secret_key=config("FLASK_SECRET_KEY")

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

# Session storage
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
