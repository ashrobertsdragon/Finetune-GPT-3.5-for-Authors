import json
import os
import secrets
import string

import chardet
from google.cloud import storage

UPLOAD_FOLDER = None
DOWNLOAD_FOLDER = None
bucket = None

# Initializatation Functions
def initialize_constants():
  """
  Initializes the global constants for the application.
  """
  UPLOAD_FOLDER = initialize_upload_folder()
  DOWNLOAD_FOLDER = initialize_GCStorage()
  

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

def initialize_GCStorage():
  """
  Initializes the Google Cloud Storage client.
  """
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
  storage_client = storage.Client()
  bucket_name = "finetuner_temp_files"
  return storage_client.bucket(bucket_name)

# Folder related functions
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

# Encoding related functions
def is_encoding(file_path: str, encoding: str) -> bool:
  """
  Checks if a file is encoded in a certain encoding.
  """
  try:
    with open(file_path, "r", encoding=encoding) as f:
      f.read()
    return True
  except UnicodeDecodeError:
    return False

def auto_detect_encoding(file_path: str) -> str:
  """
  Detects the encoding of a file using chardet.
  """
  with open(file_path, "rb") as f:
    raw_data = f.read()
  return chardet.detect(raw_data)["encoding"]

def manual_detect_encoding(file_path: str) -> str:
  """
  Manually detects the encoding of a file.
  """
  for encoding in ["iso-8859-1", "windows-1252", "utf-16", "utf-32", "iso-8859-2", "iso-8859-5", "iso-8859-6", "iso-8859-7", "iso-8859-9"]:
    if is_encoding(file_path, encoding):
      return encoding
  return ""

def recode_text(original_file_path: str) -> str:
  """
  Recodes a text file to UTF-8.
  """
  base_name, ext = os.path.splitext(original_file_path)
  recoded_file_path = f"{base_name}-recoded{ext}"
  detected_encoding = auto_detect_encoding(original_file_path) or manual_detect_encoding(original_file_path)
  with open(original_file_path, "r", encoding=detected_encoding or "utf-8", errors="ignore") as f:
    content = f.read()
  with open(recoded_file_path, "w", encoding="utf-8") as f:
    f.write(content)

# File related functions
def read_text_file(file_path: str) -> str:
  "Reads a text file and returns its content."
  with open(file_path, "r") as f:
    read_file = f.read()
  return read_file

def write_jsonl_file(content: list, file_path: str):
  "Writes a list of dictionaries to a JSONL file"
  with open(file_path, "a") as f:
    for item in content:
      json.dump(item, f)
      f.write("\n")

# GCS related functions
bucket = initialize_GCStorage()
def write_to_gcs(content: str, file: str):
  "Writes a text file to a Google Cloud Storage file."
  blob = bucket.blob(file)
  blob.upload_from_string(content, content_type="text/plain")

def upload_file_to_gcs(file_path:str, gcs_file: str):
  "Uploads a file to a Google Cloud Storage bucket"
  blob = bucket.blob(gcs_file)
  with open(file_path, "rb") as f:
    blob.upload_from_file(f, content_type="application/octet-stream")