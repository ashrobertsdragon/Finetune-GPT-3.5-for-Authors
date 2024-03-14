from decouple import config
from flask import Flask
from flask_session import Session

# Config classes for environment variables
from config import DevelopmentConfig, TestingConfig, StagingConfig, ProductionConfig

# Import blueprints
from src.accounts.views import accounts_bp
from src.binders.views import binders_bp
from src.core.views import core_bp
from src.free.views import free_bp
from src.stripe.views import stripe_bp

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
app.upload_folder=config("UPLOAD_FOLDER")
app.config["DEBUG"] = config("DEBUG", cast=bool)

# Register Blueprints
app.register_blueprint(accounts_bp)
app.register_blueprint(binders_bp)
app.register_blueprint(core_bp)
app.register_blueprint(free_bp)
app.register_blueprint(stripe_bp)

# Session storage
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Start development server
if __name__ == "__main__":
  if config("FLASK_ENV") == "development":
    app.run(debug=app.config["DEBUG"])