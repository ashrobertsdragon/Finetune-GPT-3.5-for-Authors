from flask_caching import Cache

from src import app


cache = Cache(app)