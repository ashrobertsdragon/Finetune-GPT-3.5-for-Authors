from flask import Blueprint, jsonify, render_template, session

from src.file_handling import send_file_to_bucket
from src.decorators import login_required, credit_required

from .forms import LoreBinderForm
from .utils import start_binder, str_to_dedup_list


binders_app = Blueprint("binders", __name__)

@binders_app.route("/lorebinder", methods=["GET", "POST"])
@login_required
@credit_required
def lorebinder_form_view():
    user_folder = session["user_details"]["auth_id"]
    user_email = session["user_details"]["email"]
    form = LoreBinderForm()
    if form.validate_on_submit():
        file = form.file_upload.data
        upload_path = send_file_to_bucket(user_folder, file, bucket="binders")

        title = form.title.data
        author = form.author.data
        narrator = form.narrator.data
        character_attributes_str = form.character_attributes.data
        other_attributes_str = form.other_attributes.data

        character_attributes = str_to_dedup_list(character_attributes_str)
        other_attributes = str_to_dedup_list(other_attributes_str)

        api_payload = {
            "upload_path": upload_path,
            "title": title,
            "author": author,
            "narrator": narrator,
            "character_attributes": character_attributes,
            "other_attributes": other_attributes,
            "email": user_email
        }

        response = start_binder(api_payload, endpoint_name="lorebinder")

        if response:
            message = "Your Lorebinder has been started. You should receive an email within the next hour."
            status = "success"
        else:
            message = "There was a problem starting your Lorebinder. An administrator has been contacted."
            status = "warning"
        return jsonify({"message": message, "status": status})
    
    return render_template("binders/lorebinder.html", form=form)
