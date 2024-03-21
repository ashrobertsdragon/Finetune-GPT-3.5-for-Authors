from decouple import config
from flask import Blueprint, render_template, redirect, session, url_for, flash, request


from src.supabase import supabase, update_db
from src.decorators import login_required

from .forms import SignupForm, LoginForm, AccountManagementForm, UpdatePasswordForm, BuyCreditsForm, ForgotPasswordForm
from .utils import initialize_user_db

accounts_app = Blueprint("accounts", __name__)

@accounts_app.route("/signup", methods=["GET", "POST"])
def signup_view():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            res = supabase.auth.sign_up({
                "email": email,
                "password": form.password.data,
            })
            auth_id = res.user.id
            initialize_user_db(auth_id, email)
            flash("Signup successful. Please check your email to verify your account.")
        except Exception as e:
            flash(e.message)
    
    return render_template("accounts/signup.html", form=form)

@accounts_app.route("/login", methods=["GET", "POST"])
def login_view():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            data = supabase.auth.sign_in_with_password({
                "email": form.email.data,
                "password": form.password.data
            })
            access_token = data.session.access_token
            auth_id = data.user.id
        except Exception as e:
            flash(e.message)

        session["access_token"] = access_token

        response = supabase.from_("user").select("*").eq("auth_id", auth_id).single().execute()
        user_details = response.data[0]
        session["user_details"] = user_details

        credits_available = session["user_details"]["credits_available"]
        if credits_available > 0:
            return redirect(url_for("lorebinder_form_view"))
        else:
            return redirect(url_for("buy_creditsview"))
    
    return render_template("accounts/login.html", form=form)

@accounts_app.route("/logout", methods=["GET"])
@login_required
def logout_view():
    session.pop("user_details", None)
    session.pop("access_token", None)
    supabase.auth.sign_out()
    return redirect(url_for("login_view"))

@accounts_app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_view():
    domain = config("DOMAIN")
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        return supabase.auth.reset_password_email(email, options={"redirect_to":f"{domain}/update-password.html"})
    return render_template("accounts/forgot-password.html", form=form)

@accounts_app.route("/update-password", methods=["GET", "POST"])
def reset_password_view():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data
        try:
            supabase.auth.update_user({
                "password": new_password
            })
            flash("Password successfully updated.", "success")
        except Exception:
            flash("There was a problem updating your password. Please try again.", "error")
            
    return render_template("accounts/update-password.html", form=form)


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
    account_form = AccountManagementForm()
    password_form = UpdatePasswordForm()
    if account_form.validate_on_submit():
        form = account_form
        if form.email.data:
            new_email = form.email.data
            session["user_details"]["email"] = new_email
            try:
                data = supabase.auth.update_user(
                  {"email":new_email}
                )
                access_token = data.session.access_token
                session["access_token"] = access_token
            except Exception:
                flash("Email update failed", "Error")
        session["user_details"]["f_name"] = form.first_name.data
        session["user_details"]["l_name"] = form.last_name.data
        session["user_details"]["b_day"] = form.b_day.data
        
        response = update_db()
        if response:
            flash("Your profile has been updated.", "success")
        else:
            flash("There was an error updating your profile.", "error")
    
    if password_form.validate_on_submit():
        new_password = password_form.new_password.data
        try:
            response = supabase.auth.update_user(
                {"password":new_password}
            )
            access_token = response.access_token
            session["access_token"] = access_token
            flash("Password successfully updated.", "success")
        except Exception:
            flash("There was a problem updating your password. Please try again.", "error")

    return render_template("accounts/profile.html", account_form=account_form, password_form=password_form)

@accounts_app.route("/view-binders", methods=["GET", "POST"])
@login_required
def view_binders_view():
    owner = session["user_details"]["user"]
    data = supabase.table("binderTable").select("title", "author", "download_path").filter("owner", eq=owner).execute()

    binders = [{"title": binder["title"], "author": binder["author"], "download_path": binder["download_path"]} for binder in data.data]
    return render_template("accounts/view-binders.html", binders=binders)

@accounts_app.route("/buy-credits", methods=["GET", "POST"])
@login_required
def buy_credits_view():
    form = BuyCreditsForm()
    if form.validate_on_submit():
        num_credits = form.credits.data
        return redirect(f"/checkout.html?num_credits={num_credits}")
    return render_template("accounts/buy_credits.html", form=form)
