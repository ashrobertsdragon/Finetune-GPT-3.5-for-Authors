from flask import Blueprint, render_template, session

from src import app
from src.utils import login_required, credit_required, upload_supabase_bucket

from .credits import update_credits
from .forms import LoreBinderForm
from .utils import call_api, save_binder_data


binders_bp = Blueprint("binders", __name__)

@app.route("/lorebinder", method=["GET", "POST"])
@login_required
@credit_required
def lorebinder_form_view():
    user = session["user_details"]["user"]
    user_folder = session["user_details"]["uuid"]
    user_email = session["user_details"]["email"]
    form = LoreBinderForm
    if form.validate_on_submit():
        file = form.file_upload.data
        upload_path = upload_supabase_bucket(user_folder, file, bucket="binders")

        title = form.title.data
        author = form.author.data
        narrator = form.narrator.data
        character_attributes = form.character_attributes.data
        other_attributes = form.other_attributes.data

        api_payload = {
            "upload_path": upload_path,
            "title": title,
            "author": author,
            "narrator": narrator,
            "character_attributes": character_attributes,
            "other_attributes": other_attributes,
            "email": user_email
        }

        call_api(api_payload)
        save_binder_data(api_payload, user)
        update_credits(user)
    
    render_template("lorebinder.html", form=form)
