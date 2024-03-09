import os
from flask import Flask
from flask_session import Session

# Blueprints
from src.accounts.views import accounts_bp
from src.binders.views import binders_bp
from src.core.views import core_bp
from src.free.views import free_bp

app = Flask(__name__)
app.secret_key=os.environ["FLASK_SECRET_KEY"]

# Register Blueprints
app.register_blueprint(accounts_bp)
app.register_blueprint(binders_bp)
app.register_blueprint(core_bp)
app.register_blueprint(free_bp)

# Session storage
app.config["SESSION_TYPE"] = "filesystem"
Session(app)