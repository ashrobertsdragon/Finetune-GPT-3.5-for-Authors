import logging
import os
import secrets
import string
import threading

import requests
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile

from logging_config import start_loggers
from ebook_conversion.convert_file import convert_file
from file_handling import is_encoding, initialize_GCStorage
from finetune.shared_resources import training_status
from finetune.training_management import train
from send_email import send_mail
from forms import ContactForm, FineTuneForm, EbookConversionForm

load_dotenv()
# Set up Logging
start_loggers()
error_logger = logging.getLogger('error_logger')

def initialize_upload_folder():
  """
  Determines if the environment is production or development and sets the path
  to the upload folder accordingly.
  """
  if os.environ.get("FLASK_ENV") == "production":
    UPLOAD_FOLDER = os.path.join("/tmp", "upload")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
  else:
    UPLOAD_FOLDER = os.path.join("app", "upload_folder")
  return UPLOAD_FOLDER

def random_str():
  return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def make_folder() -> tuple[str, str]:
  """
  Generates a random string and creates a folder with that string in the upload
  folder. Returns the path to the folder and the random string.
  """
  temp_folder = random_str()
  folder_name = os.path.join(UPLOAD_FOLDER, temp_folder)
  try:
    os.makedirs(folder_name)
  except OSError:
    return make_folder()
  return folder_name, temp_folder

app = Flask(__name__)

UPLOAD_FOLDER = initialize_upload_folder()
DOWNLOAD_FOLDER = initialize_GCStorage()
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

app.config["SECRET_KEY"]=os.environ.get("FLASK_SECRET_KEY")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


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
  form = ContactForm()
  def check_email(user_email: str) -> bool:
    api_key =  os.environ.get("abstract_api_key")
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={api_key}&email={user_email}"
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
  
  if form.validate_on_submit():
    name = form.name.data
    user_email = form.email.data
    message = form.message.data
    threading.Thread(target=send_message, args=(name, user_email, message)).start()

  return render_template("contact-us.html", form=form)

@app.route("/convert-ebook", methods=["GET", "POST"])
def convert_ebook():
  form=EbookConversionForm()
  supported_mimetypes = [
    "application/epub+zip", 
    "application/pdf", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
  ]

  if form.validate_on_submit():
    uploaded_file = form.ebook.data
    title = form.title.data
    author = form.author.data

    if uploaded_file:
      if uploaded_file.mimetype not in supported_mimetypes:
        return jsonify({"error": "Unsupported file type"}), 400

      folder_name, _ = make_folder()
      file_path = os.path.join(folder_name, uploaded_file.filename)
      uploaded_file.save(file_path)
      if uploaded_file.mimetype == "text/plain" and not is_encoding(file_path, "utf-8"):
        error_logger.error(f"{file_path} is not UTF-8")
        return jsonify({"error": "Not correct kind of text file. Please resave as UTF-8"}), 400

      metadata = {"title": title, "author": author}
      book_name, psuedopath = convert_file(file_path, metadata)

      with NamedTemporaryFile() as temp_file:
        blob = DOWNLOAD_FOLDER.blob(psuedopath)
        blob.download_to_filename(temp_file.name)

        return send_file(path_or_file=temp_file.name, as_attachment="True", attachment_filename=book_name)

  return render_template("convert-ebook.html", form=form)

@app.route("/finetune", methods=["GET", "POST"])
def finetune():
  form = FineTuneForm()
  if form.validate_on_submit():
    role = form.role.data
    chunk_type = form.chunk_type.data
    user_key = form.user_key.data

    # Validate user key
    if not (user_key.startswith("sk-") and 50 < len(user_key) < 60):
      error_logger.error("invalid key")
      return jsonify({"error": "Invalid user key"}), 400

    folder_name, user_folder = make_folder()

    files = request.files.getlist("file")
    if not files:
      return jsonify({"error": "No files uploaded"}), 400
    for file in files:
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

        if not is_encoding(file_path, "utf-8"):
          os.remove(file_path)
          error_logger.error(f"{file_path} is not UTF-8")
          return jsonify({"error": "Not correct kind of text file. Please resave as UTF-8"}), 400
      else:
        error_logger.error("File is not text file")

    threading.Thread(target=train, args=(folder_name, role, user_key, chunk_type, user_folder)).start()
    return jsonify({"success": True, "user_folder": user_folder}) 

  return render_template("finetune.html", form=form)

@app.route('/status', methods=['POST'])
def status():
  data = request.get_json()
  user_folder = data.get('user_folder')
  return jsonify({"status": training_status.get(user_folder, "Not started")})
