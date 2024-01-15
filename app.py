import os
import uuid
import threading

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

@app.route("/", methods=["GET", "POST"])
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
    return render_template("index.html", folder_name=folder_name.split("/")[-1])

  return render_template("index.html")

@app.route("/status/<folder_name>")
def status(folder_name: str):
    full_path = os.path.join(UPLOAD_FOLDER, folder_name)
    return jsonify({"status": training_status.get(full_path, "Not started")})

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/convert-ebook', methods=['GET', 'POST'])
def convert_ebook():
    if request.method == 'POST':
        uploaded_file = request.files.get('ebook')
        title = request.form.get('title')
        author = request.form.get('author')

        if uploaded_file:
            unique_folder = str(uuid.uuid4())
            os.makedirs(unique_folder, exist_ok=True)
            filepath = os.path.join(unique_folder, uploaded_file.filename)
            uploaded_file.save(filepath)

            metadata = {'title': title, 'author': author}
            output_filepath = convert_file(unique_folder, filepath, metadata)

            @after_this_request
            def cleanup(response):
                os.remove(filepath)
                os.remove(output_filepath)
                os.remove(unique_folder)
                return response

            return send_from_directory(directory=unique_folder, filename=os.path.basename(output_filepath), as_attachment=True)

    return render_template('convert_ebook.html')
