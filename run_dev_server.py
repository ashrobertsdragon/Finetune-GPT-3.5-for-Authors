from decouple import config

from prosepal import app

# Start development server
if __name__ == "__main__" and config("FLASK_ENV") == "development":
    app.run(debug=True)
