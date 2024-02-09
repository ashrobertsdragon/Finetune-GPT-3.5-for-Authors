import logging
import os
import secrets
import string
import threading

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

def random_str():
  return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))

@app.route('/')
def landing_page():
  return render_template("index.html")

@app.route("/finetune/instructions")
def instructions():
  return render_template("instructions.html")

@app.route("/privacy")
def privacy_page():
  return send_from_directory("static","html/privacy.html")

@app.route("/terms")
def terms_of_service():
  return send_from_directory("static", "html/terms.html")

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

      flask_folder_name = os.path.join("upload_folder", random_str())
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
      return jsonify({"error": "Invalid user key"}), 400

    folder_name = os.path.join(UPLOAD_FOLDER, random_str())
    os.makedirs(folder_name, exist_ok=True)

    for file in request.files.getlist("file"):
      if (
        file
        and file.filename.endswith(("txt", "text"))
        and file.mimetype == "text/plain"
      ):
        random_filename = f"{random_str()}.txt"
        file_path = os.path.join(folder_name, random_filename)
        file.save(file_path)

        file_size = os.path.getsize(file_path)
        min_size = 1024 # 1 KB
        max_size = 1024 * 1024 # 1 MB
        if file_size < min_size or file_size > max_size:
          os.remove(file_path)
          error_logger.error(f"{file_path} has an invalid size")
          return jsonify({"error": "Invalid file size"}), 400

        if not is_utf8(file_path):
          os.remove(file_path)
          error_logger.error(f"{file_path} is not UTF-8")
          return jsonify({"error": "Not correct kind of text file. Please resave as UTF-8"}), 400
      else:
        error_logger.error("File is not text file")

    threading.Thread(target=train, args=(folder_name, role, user_key, chunk_type)).start()
    return jsonify({"success": True, "user_folder": folder_name.split("/")[-1]}) 

  return render_template("finetune.html")

@app.route('/status', methods=['POST'])
def status():
  data = request.get_json()
  user_folder = data.get('user_folder')
  print(training_status[user_folder])
  return jsonify({"status": training_status.get(user_folder, "Not started")})

@app.route("/download/<path:download_path>")
def download_file(download_path:str):
  flask_path = os.path.join("upload_folder", download_path)
  return send_file(flask_path, as_attachment=True)

