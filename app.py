import logging
import os
import threading
import uuid

import requests
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory

from cleanup import cleanup_directory
from logging_config import start_loggers
from ebook_conversion.convert_file import convert_file
from file_handling import is_utf8
from finetune.shared_resources import training_status
from finetune.training_management import train
from send_email import send_mail


start_loggers()
error_logger = logging.getLogger('error_logger')

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join("app", "upload_folder")
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
cleanup_thread = threading.Thread(target=cleanup_directory, args=(UPLOAD_FOLDER,), daemon=True).start()

@app.route("/favicon.ico")
def favicon():
  return send_from_directory(os.path.join(app.root_path, "static"),
                            "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/apple-touch-icon.png")
def apple_favicon():
  return send_from_directory(os.path.join(app.root_path, "static"), 
                            "apple-touch-icon.png", mimetype="image/png")

@app.route("/finetune/instructions")
def instructions():
  return send_from_directory(os.join.path(app.root_path, "static"),
                            "instructions.html", mimetype="text/html")

@app.route("/privacy")
def privacy_page():
  return send_from_directory(os.join.path(app.root_path, "static"),
                            "privacy.html", mimetype="text/html")

@app.route("/terms")
def terms_of_service():
  return send_from_directory(os.join.path(app.root_path, "static"),
                            "terms.html", mimetype="text/html")

@app.route("/contact-us", methods=["GET", "POST"])
def send_email():
  def check_email(user_email: str) -> bool:
    api_key =  os.getenv("abstract_api_key")
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={api_key}&{user_email}"
    response = requests.get(url).json()
    if response.get("deliverability") != "DELIVERABLE":
      return False
    if not response.get("is_valid_format", {}).get("value"):
      return False
    if not response.get("is_smtp_valid", {}).get("value"):
      return False
    return True
  def send_message(name, user_email, message) -> None:
    if check_email(user_email):
      send_mail(name, user_email, message)
  
  if request.method == "POST":
    name = request.form.get("name")
    user_email = request.form.get("email")
    message = request.form.get("message")
    threading.Thread(target=send_message, args=(name, user_email, message)).start()

  return render_template("contact-us.html")

@app.route("/convert-ebook", methods=["GET", "POST"])
def convert_ebook():

  supported_mimetypes = [
    "application/epub+zip", 
    "application/pdf", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
  ]
  if request.method == "POST":
    uploaded_file = request.files.get("ebook")
    title = request.form.get("title")
    author = request.form.get("author")
    if uploaded_file:
      if uploaded_file.mimetype not in supported_mimetypes:
        return jsonify({"error": "Unsupported file type"}), 400
      
      unique_folder = str(uuid.uuid4())
      flask_folder_name = os.path.join("upload_folder", unique_folder)
      absolute_folder_name = os.path.join("app", flask_folder_name)
      os.makedirs(absolute_folder_name, exist_ok=True)
      absolute_filepath = os.path.join(absolute_folder_name, uploaded_file.filename)
      uploaded_file.save(absolute_filepath)

      metadata = {"title": title, "author": author}
      output_file = convert_file(absolute_filepath, metadata)
      flask_output_filepath = os.path.join(flask_folder_name, output_file)

      return send_file(path_or_file=flask_output_filepath, mimetype="text/plain", as_attachment="True", max_age=None)

  return render_template("convert-ebook.html")

@app.route("/finetune", methods=["GET", "POST"])
def finetune():
  if request.method == "POST":
    role = request.form["role"]
    chunk_type = request.form["chunk_type"]
    user_key = request.form["user_key"]

    # Validate user key
    if not (user_key.startswith("sk-") and 50 < len(user_key) < 60):
      error_logger.error("invalid key")
      return "Invalid user key", 400

    folder_name = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(folder_name, exist_ok=True)

    for file in request.files.getlist("file"):
      if (
        file
        and file.filename.endswith(("txt", "text"))
        and file.mimetype == "text/plain"
      ):
        random_filename = f"{str(uuid.uuid4())}.txt"
        file_path = os.path.join(folder_name, random_filename)
        file.save(file_path)

        if not is_utf8(file_path):
          os.remove(file_path)
          error_logger.error(f"{file_path} is not UTF-8")
          return "File is not UTF-8 encoded", 400
  
    threading.Thread(target=train, args=(folder_name, user_key, role, chunk_type)).start()
    return render_template("finetune.html", folder_name=folder_name.split("/")[-1])

  return render_template("finetune.html")

@app.route("/status/<folder_name>")
def status(folder_name: str):
  return jsonify({"status": training_status.get(folder_name, "Not started")})

@app.route("/download/<path:download_path>")
def download_file(download_path):
  flask_path = os.path.join("upload_folder", download_path)
  return send_file(flask_path, as_attachment=True)

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)