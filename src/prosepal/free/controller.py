import os
from io import BytesIO
from pathlib import Path

from flask import current_app, jsonify, request
from flask.wrappers import Response
from flask_wtf import FlaskForm
from werkzeug.datastructures.file_storage import FileStorage
from werkzeug.utils import secure_filename

from . import utils
from .utils import ChunkType


def process_finetune_submission(form: FlaskForm) -> tuple[Response, int]:
    """
    Process the Finetuner form submission and calls the API for fine-tuning
    an LLM.

    Args:
        form (FlaskForm): The form object.

    Returns:
        tuple[Response, int]: A JSON response and HTTP status code
    """
    user_key: str = form.user_key.data
    if not utils.is_valid_user_key(user_key):
        return jsonify({"error": "Invalid user key"}), 400

    folder_name, user_folder = utils.make_folder()
    files: list[FileStorage] = request.files.getlist("file")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    for file in files:
        processed: tuple[Response, int] | Path = process_finetune_file(
            file, folder_name, form.role.data, form.chunk_type.data
        )
        if isinstance(processed, tuple):  # Error occurred
            return processed

    utils.call_finetune_api(
        processed,
        model=form.model.data,
        user_key=form.user_key.data,
    )

    return jsonify({"success": True, "user_folder": user_folder}), 200


def save_file(
    file: FileStorage, folder_name: Path, extension: str
) -> tuple[Response, int] | Path:
    """
    Saves the file to a temporary folder with a random string for a filename.

    Args:
        file (FileStorage): The uploaded file.
        folder_name (Path): The Path object for the temporary upload folder.
        extension (str): The extension the file should be saved with.

    Returns:
        tuple[Response, int] | Path: If there is an error, a JSON response
            object and HTTP status 400 are returned. Otherwise, the Path
            object for the file to be processed.
    """
    random_filename = f"{utils.random_str()}.{extension}"
    file_path = Path(folder_name, secure_filename(random_filename))
    file.save(file_path)

    if not utils.is_valid_file_size(file_path):
        file_path.unlink()
        current_app.logger.error("Invalid file size")
        return jsonify({"error": "Invalid file size"}), 400
    return file_path


def auto_chunk_text_file(
    file: FileStorage, folder_name: Path, sys_role: str, chunk_type: ChunkType
) -> tuple[Response, int] | Path:
    """
    Process a text file and sent it to the auto-chunking API to get a JSONL
    file for fine-tuning.

    Args:
        file (FileStorage): The uploaded file.
        folder_name (Path): The Path object for the temp folder to save the
        file to.
        sys_role (str): The system message for fine tuning.
        chunk_type (ChunkType): Enum of auto-chunking method to be used
            on text file.

    Returns:
        tuple[Response, int] | Path: If there is an error, a JSON response
            object and HTTP status 400 are returned. Otherwise, the Path
            object for the file ready to send to the fine-tuning API.
    """
    if sys_role is None:
        current_app.logger.error("System message must be set")
        return jsonify({"error": "System message must be set"}), 400
    if ChunkType == ChunkType.NONE:
        current_app.logger.error("Chunk type must be set")
        return jsonify({"error": "Chunk type must be set"}), 400

    file_path: tuple[Response, int] | Path = save_file(
        file, folder_name, extension="txt"
    )
    if isinstance(file_path, tuple):  # This is an error message
        return file_path
    if not utils.is_encoding(file_path, "utf-8"):
        os.remove(file_path)
        current_app.logger.error(f"{file_path} is not UTF-8")
        return jsonify(
            {"error": "Not correct kind of text file. Please resave as UTF-8"}
        ), 400
    jsonl_file: BytesIO = utils.call_api(
        "finetuner", file_path, sys_role=sys_role, chunk_type=chunk_type.value
    )
    return save_file(jsonl_file, folder_name, "jsonl")


def process_finetune_file(
    file: FileStorage,
    folder_name: Path,
    sys_role: str | None = None,
    chunk_type: ChunkType = ChunkType.NONE,
) -> tuple[Response, int] | Path:
    """
    Processes the uploaded file for fine-tuning, running text files through
    the auto-chunking API.

    Args:
    file (FileStorage): The uploaded file.
    folder_name (Path): The Path object for the temp folder to save the file
        to.
    sys_role (str): Optional. The system message for fine tuning. Defaults to
        None to allow for JSONL files to be uploaded.
    chunk_type (ChunkType): Optional. Enum of auto-chunking method to be used
        on text file. Defaults to ChunkType.NONE to allow for JSONL files to
        be uploaded.

    Returns:
        tuple[Response, int] | Path: If there is an error, a JSON response
            object and HTTP status 400 are returned. Otherwise, the Path
            object for the file ready to send to the fine-tuning API.
    """
    if file:
        if (
            file.filename.endswith(("txt", "text"))
            and file.mimetype == "text/plain"  # noqa: W503
        ):
            jsonl_file: tuple[Response, int] | Path = auto_chunk_text_file(
                file, folder_name, sys_role, chunk_type
            )

        if file.filename.endswith("jsonl"):
            jsonl_file = save_file(file, folder_name, extension="jsonl")
        return jsonl_file

    current_app.logger.error("File is not text or jsonl file")
    return jsonify({"error": "File is not text or jsonl file"}), 400


def process_file_before_conversion(
    file: FileStorage,
) -> tuple[Response, int] | Path:
    supported_mimetypes: list[str] = [
        "application/epub+zip",
        "application/pdf",
        (
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        "text/plain",
    ]

    if file.mimetype not in supported_mimetypes:
        current_app.logger.error(
            f"Unsupported file type. Received type {file.mimetype}"
        )
        return jsonify(
            {"error": "Unsupported file type. Must be epub, docx, pdf, or txt"}
        ), 400

    folder_name, _ = utils.make_folder()
    file_path = Path(folder_name, file.filename)
    file.save(file_path)

    if file.mimetype == "text/plain" and not utils.is_encoding(
        file_path, "utf-8"
    ):
        file_path.unlink()
        current_app.logger.error(f"{file_path} is not UTF-8")
        error_msg = "Not correct kind of text file. " "Please resave as UTF-8"
        return jsonify({"error": error_msg}), 400
    return file_path


def process_convert_ebook_submission(
    form: FlaskForm,
) -> tuple[str, Path] | tuple[Response, int]:
    if uploaded_file := form.ebook.data:
        file_path = process_file_before_conversion(uploaded_file)
        if isinstance(file_path, tuple):  # Error response
            return file_path

        title: str = form.title.data
        author: str = form.author.data

        metadata: dict[str, str] = {"title": title, "author": author}

        return utils.convert_ebook(file_path, metadata)
