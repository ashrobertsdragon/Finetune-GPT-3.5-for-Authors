import os
import uuid
import threading
import time

from flask import Flask, render_template, request, jsonify, send_from_directory, after_this_request

from convert_file import convert_file
from file_handling import is_utf8
from shared_resources import training_status
from training_management import train


app = Flask(__name__)
UPLOAD_FOLDER = os.path.join("prosepal", "upload_folder")
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

@app.route("/finetune", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    role = request.form["role"]
    chunk_type = request.form["chunk_type"]
    user_key = request.form["user_key"]

    # Validate user key
    if not (user_key.startswith("sk-") and 50 < len(user_key) > 60):
      return "Invalid user key", 400

    folder_name = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(folder_name, exist_ok=True)

    for file in request.files.getlist("file"):
      if file and file.filename.endswith(("txt", "text")):
        random_filename = f"{str(uuid.uuid4())}.txt"
        file_path = os.path.join(folder_name, random_filename)
        file.save(file_path)

        if not is_utf8(file_path):
          os.remove(file_path)
          return "File is not UTF-8 encoded", 400
                    
    threading.Thread(target=train, args=(folder_name, user_key, role, chunk_type)).start()
    return render_template("finetune.html", folder_name=folder_name.split("/")[-1])

  return render_template("finetune.html")

@app.route("/status/<folder_name>")
def status(folder_name: str):
    full_path = os.path.join(UPLOAD_FOLDER, folder_name)
    return jsonify({"status": training_status.get(full_path, "Not started")})

@app.route('/convert-ebook', methods=['GET', 'POST'])
def convert_ebook():
    if request.method == 'POST':
        uploaded_file = request.files.get('ebook')
        title = request.form.get('title')
        author = request.form.get('author')

        if uploaded_file:
            unique_folder = str(uuid.uuid4())
            folder_name = os.path.join("upload_folder", unique_folder)
            absolute_folder_name = os.path.join("app", folder_name)
            os.makedirs(absolute_folder_name, exist_ok=True)
            filepath = os.path.join(absolute_folder_name, uploaded_file.filename)
            uploaded_file.save(filepath)

            metadata = {'title': title, 'author': author}
            output_file = convert_file(filepath, metadata)

            @after_this_request
            def cleanup(response):
              time.sleep(10)
              output_filepath = os.path.join(absolute_folder_name, output_file)
              os.remove(filepath)
              os.remove(output_filepath)
              os.remove(absolute_folder_name)
              return response

            return send_from_directory(directory=folder_name, path=output_file, as_attachment=True)

    return render_template('convert-ebook.html')

if __name__ == "__main__":
    app.run(debug=True)