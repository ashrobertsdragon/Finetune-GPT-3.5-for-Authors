import os
import uuid
import threading

from openai import OpenAI
from flask import Flask, render_template, request, jsonify

from data_preparation import is_utf8
from training_management import train


app = Flask(__name__)
training_status = {}
client = OpenAI()
UPLOAD_FOLDER = os.path.join("prosepal", "upload_folder")
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    role = request.form["role"]
    chunk_type = request.form["chunk_type"]
    user_key = request.form["user_key"]

    # Validate user key
    if not (user_key.startswith("sk-") and 50 < len(user_key) > 60):
      return "Invalid user key", 400

    random_folder = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(random_folder, exist_ok=True)

    for file in request.files.getlist("file"):
      if file and file.filename.endswith(("txt", "text")):
        random_filename = f"{str(uuid.uuid4())}.txt"
        file_path = os.path.join(random_folder, random_filename)
        file.save(file_path)

        if not is_utf8(file_path):
          os.remove(file_path)
          return "File is not UTF-8 encoded", 400
                    
    threading.Thread(target=train, args=(random_folder, user_key, role, chunk_type)).start()
    return render_template("index.html", folder_name=random_folder.split("/")[-1])

  return render_template("index.html")

@app.route("/status/<folder_name>")
def status(folder_name: str):
    full_path = os.path.join(UPLOAD_FOLDER, folder_name)
    return jsonify({"status": training_status.get(full_path, "Not started")})

if __name__ == "__main__":
    app.run(debug=True)
