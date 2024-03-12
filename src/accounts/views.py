from flask import Blueprint, render_template, redirect, jsonify, session, url_for, flash


from src import app
from src.supabase_client import supabase
from src.utils import login_required
from .forms import SignupForm, LoginForm, AccountManagementForm, UpdatePasswordForm, BuyCreditForm
from .utils import add_extra_user_info

accounts_bp = Blueprint("accounts", __name__)

@app.route("/signup", methods=["GET", "POST"])
def signup_view():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        res = supabase.auth.sign_up({
            "email": email,
            "password": form.password.data,
        })
        if res.error:
            return jsonify({"error": {res.error.message}}), res.error.status
        else:
            user_id  = res.data["user"].get("id")
            add_extra_user_info(user_id, email)
            return jsonify({"success": True, "message": "Signup successful. Please check your email to verify your account."}), 200
    
    return render_template("signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_view():
    form = LoginForm()
    if form.validate_on_submit():
        data = supabase.auth.sign_in_with_password({
            "email": form.email.data,
            "password": form.password.data
        })
        if data.error:
            return jsonify({"error": {data.error.message}}), data.error.status
        
        auth_id = data.user.id
        access_token = data.data.access_token

        session["access_token"] = access_token
        session["auth_id"] = auth_id

        response = supabase.from_("user").select("*").eq("auth_id", auth_id).single().execute()
        user_details = response.data[0]
        session["user_details"] = user_details

        credits_available = session["user_details"]["credits_available"]
        if credits_available > 0:
            return redirect("lorebinder.html")
        else:
            return redirect("account.html#but_credits")
    
    return render_template("login.html", form=form)

@app.route("/logout", method=["GET"])
@login_required
def logout_view():
    session.pop("user_details", None)
    session.pop("auth_id", None)
    session.pop("access_token", None)
    supabase.auth.sign_out()
    return redirect("/login.html")

@app.route("/account")
@login_required
def account_view():
    pass
"""

    if section == "profile":
        return profile()
    elif section == "view_binders":
        return view_binders()
    elif section == "buy_credits":
        return buy_credits()
    else:
        return redirect(url_for("account_view", section="profile"))
"""

@app.route("/profile")
@login_required
def profile_view():
    user_id = session["user_details"]["id"]
    account_form = AccountManagementForm()
    password_form = UpdatePasswordForm()
    if account_form.validate_on_submit():
        form = account_form
        update_user = {}
        if form.email.data:
            new_email = form.email.data
            supabase.table("user").update({"email": new_email}).eq("user_id", user_id).execute()
            supabase.auth.update_user(
              access_token=session["access_token"],
              email=new_email
            )
        if form.first_name.data:
            update_user["f_name"] = form.first_name.data
            session["user_details"]["f_name"] = form.first_name.data
        if form.last_name.data:
            update_user["l_name"] = form.last_name.data
            session["user_details"]["l_name"] = form.last_name.data
        if form.b_day.data:
            update_user["b_day"] = form.b_day.data
            session["user_details"]["b_day"] = form.b_day.data
        if update_user:
            error, _ = supabase.table("userTable").update(update_user).eq("user_id", user_id).execute()

            if error:
                flash("There was an error updating your profile.", "error")
            else:
                flash("Your profile has been updated.", "success")

        return redirect(url_for("account_view", section="profile"))
    
    if password_form.validate_on_submit():
        new_password = password_form.new_password.data
        error = supabase.auth.update_user(
            access_token=session["access_token"],
            password=new_password
        )

        if error:
            flash("There was a problem updating your password. Please try again.", "error")
        else:
            flash("Password successfully updated.", "success")

    return render_template("profile.html", account_form=account_form, password_form=password_form)

@app.route("/view-binders", method=["GET", "POST"])
@login_required
def view_binders_view():
    owner = session["user_details"]["user"]
    data = supabase.table("binderTable").select("title", "author", "download_path").filter("owner", eq=owner).execute()

    binders = [{"title": binder["title"], "author": binder["author"], "download_path": binder["download_path"]} for binder in data.data]
    return render_template("view-binders.html", binders=binders)

@app.route("/buy-credits")
@login_required
def buy_credits_view():
    form=BuyCreditForm()
    render_template("buy_credits.html", form=form)