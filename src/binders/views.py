import requests
from flask import Blueprint, render_template, redirect, session

from src import app
from src.supabase_client import supabase
from src.utils import login_required, credit_required, upload_supabase_bucket, send_mail
from .forms import LoreBinderForm

binders_bp = Blueprint("binders", __name__)

@app.route("/lorebinder", method=["GET", "POST"])
@login_required
@credit_required
def lorebinder_form_view():
    user = session["user_details"]["uuid"]
    form = LoreBinderForm
    if form.validate_on_submit():
        file = form.file_upload.data
        upload_path = upload_supabase_bucket(user, file, bucket="binders")

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
            "other_attributes": other_attributes
        }
        response = requests.post('PP_API_ENDPOINT', json=api_payload)
        if response.status_code != 200:
            send_mail(f"{response.message} for {api_payload}")

        api_payload["owner"] = user
        try:
            supabase.table("binderTable").insert(api_payload).execute()
        except Exception as e:
            send_mail(f"Exception {e} saving {api_payload} to binderTable")
            
        return redirect("lorebinder-success.html")
    
    render_template("lorebinder.html", form=form)
