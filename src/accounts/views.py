from decouple import config
from flask import Blueprint, render_template, redirect, jsonify, session, url_for, flash, request


from src.supabase import supabase, update_db
from src.utils import login_required

from .forms import SignupForm, LoginForm, AccountManagementForm, UpdatePasswordForm, BuyCreditForm, ForgotPasswordForm
from .utils import initialize_user_db

accounts_app = Blueprint("accounts", __name__, template_folder="templates/accounts")

@accounts_app.route("/signup", methods=["GET", "POST"])
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
            initialize_user_db(user_id, email)
            return jsonify({"success": True, "message": "Signup successful. Please check your email to verify your account."}), 200
    
    return render_template("signup.html", form=form)

@accounts_app.route("/login", methods=["GET", "POST"])
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
            return redirect(url_for("lorebinder_form_view"))
        else:
            return redirect(url_for("buy_creditsview"))
    
    return render_template("login.html", form=form)

@accounts_app.route("/logout", method=["GET"])
@login_required
def logout_view():
    session.pop("user_details", None)
    session.pop("auth_id", None)
    session.pop("access_token", None)
    supabase.auth.sign_out()
    return redirect(url_for("login_view"))

@accounts_app.route("/forgot-password", method=["GET", "POST"])
def forgot_password_view():
    domain = config("DOMAIN")
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        return supabase.auth.reset_password_for_email(email, redirect_to=f"{domain}/update-password")
    return render_template("forgot-password.html", form=form)

@accounts_app.route("/account", methods=["GET", "POST"])
@login_required
def account_view():
    section = request.args.get("section", "profile")
    if section == "profile":
        return profile_view()
    elif section == "view-binders":
        return view_binders_view()
    elif section == "buy-credits":
        return buy_credits_view()
    else:
        return redirect(url_for("account_view", section="profile"))

@accounts_app.route("/profile")
@login_required
def profile_view():
    user_id = session["user_details"]["id"]
    account_form = AccountManagementForm()
    password_form = UpdatePasswordForm()
    if account_form.validate_on_submit():
        form = account_form
        if form.email.data:
            new_email = form.email.data
            session["user_details"]["email"] = new_email
            supabase.table("user").update({"email": new_email}).eq("user_id", user_id).execute()
            supabase.auth.update_user(
              access_token=session["access_token"],
              email=new_email
            )
        session["user_details"]["f_name"] = form.first_name.data
        session["user_details"]["l_name"] = form.last_name.data
        session["user_details"]["b_day"] = form.b_day.data
        
        error, success = update_db()
        if error:
            flash("There was an error updating your profile.", "error")
        if success:
            flash("Your profile has been updated.", "success")
    
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

@accounts_app.route("/view-binders", method=["GET", "POST"])
@login_required
def view_binders_view():
    owner = session["user_details"]["user"]
    data = supabase.table("binderTable").select("title", "author", "download_path").filter("owner", eq=owner).execute()

    binders = [{"title": binder["title"], "author": binder["author"], "download_path": binder["download_path"]} for binder in data.data]
    return render_template("view-binders.html", binders=binders)

@accounts_app.route("/buy-credits", method=["GET", "POST"])
@login_required
def buy_credits_view():
    form = BuyCreditForm()
    if form.validate_on_submit():
        num_credits = form.credits.data
        return redirect(f"/checkout.html?num_credits={num_credits}")
    return render_template("buy_credits.html", form=form)
