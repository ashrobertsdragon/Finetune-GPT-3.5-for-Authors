from pathlib import Path

from flask import Blueprint, jsonify, render_template, request, send_file

# from prosepal.exceptions import APIError
from prosepal.free import utils

from .controller import (
    process_convert_ebook_submission,
    process_finetune_submission,
)
from .forms import EbookConversionForm, FineTuneForm, JSONLConversionForm

free_app = Blueprint("free", __name__)


def training_status():
    pass  # dummy function till API is implemented


@free_app.route("/create-jsonl", methods=["GET", "POST"])
def create_jsonl():
    form = JSONLConversionForm()
    if form.validate_on_submit():
        if uploaded_file := form.csv.data:
            filename: str = Path(uploaded_file.filename).stem
            return_file = utils.call_jsonl_api(uploaded_file)
            return send_file(
                return_file,
                as_attachment=True,
                download_name=f"{filename}.jsonl",
                mimetype="application/octet-stream",
            )
    return render_template("free/create-jsonl.html", form=form)


@free_app.route("/convert-ebook", methods=["GET", "POST"])
def convert_ebook():
    form = EbookConversionForm()
    if form.validate_on_submit():
        book_name, download_path = process_convert_ebook_submission(form)
        return send_file(
            path_or_file=download_path,
            as_attachment="True",
            download_name=book_name,
        )

    return render_template("free/convert-ebook.html", form=form)


@free_app.route("/finetune", methods=["GET", "POST"])
def finetune():
    form = FineTuneForm()
    if form.validate_on_submit():
        return process_finetune_submission(form)
    return render_template("free/finetune.html", form=form)


@free_app.route("/status", methods=["POST"])
def status():
    data = request.get_json()
    user_folder = data.get("user_folder")
    return jsonify({"status": training_status.get(user_folder, "Not started")})


@free_app.route("/finetune/instructions", methods=["GET"])
def finetune_instructions():
    return render_template("free/instructions.html")


@free_app.route("/free", methods=["GET"])
def free_page():
    return render_template("free/free.html")
