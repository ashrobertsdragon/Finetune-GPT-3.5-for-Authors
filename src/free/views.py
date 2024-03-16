import os
import logging
from flask import Blueprint, request, render_template, jsonify

from src.utils import random_str
from src.logging_config import start_loggers

from .forms import EbookConversionForm, FineTuneForm
from src.free.utils import make_folder, is_encoding

free_app = Blueprint("free", __name__)

start_loggers()
error_logger = logging.getLogger("error_logger")

def training_status():
    pass # dummy function till API is implemented

@free_app.route("/convert-ebook", methods=["GET", "POST"])
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
            print(metadata) # All this is changing 
            """
            book_name, psuedopath = convert_file(file_path, metadata)

            with NamedTemporaryFile() as temp_file:
                blob = DOWNLOAD_FOLDER.blob(psuedopath)
                blob.download_to_filename(temp_file.name)

                return send_file(path_or_file=temp_file.name, as_attachment="True", download_name=book_name)
"""
    return render_template("free/convert-ebook.html", form=form)

@free_app.route("/finetune", methods=["GET", "POST"])
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
        def call_api(folder_name, role, user_key, chunk_type, user_folder):
            pass # placeholder
        call_api(folder_name, role, user_key, chunk_type, user_folder)

        return jsonify({"success": True, "user_folder": user_folder}) 

    return render_template("free/finetune.html", form=form)

@free_app.route("/status", methods=["POST"])
def status():
    data = request.get_json()
    user_folder = data.get("user_folder")
    return jsonify({"status": training_status.get(user_folder, "Not started")})

@free_app.route("/finetune/instructions", methods=["GET"])
def instructions():
    return render_template("free/instructions.html")
