from decouple import config
from src import app

# Start development server
if __name__ == "__main__":
  if config("FLASK_ENV") == "development":
    app.run(debug=True)