from flask import (Blueprint, current_app, flash, render_template, redirect,
                  request, session, url_for)

from src.supabase import SupabaseAuth
from src.decorators import login_required
from src.utils import update_db

from .forms import (AccountManagementForm, BuyCreditsForm, ForgotPasswordForm,
                    LoginForm, SignupForm, UpdatePasswordForm)
from .utils import get_binders, initialize_user_db, redirect_after_login

accounts_app = Blueprint("accounts", __name__)

auth = SupabaseAuth()

@accounts_app.route("/signup", methods=["GET", "POST"])
def signup_view():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            res = auth.sign_up(email=email, password=form.password.data)
            auth_id = res.user.id
            initialize_user_db(auth_id, email)
            flash(
                "Signup successful."
                "Please check your email to verify your account."
                )
        except Exception as e:
            flash(e.message)
    
    return render_template("accounts/signup.html", form=form)

@accounts_app.route("/login", methods=["GET", "POST"])
def login_view():
    if "access_token" in session and "user_details" in session:
        auth_id = session["user_details"]["auth_id"]
        redirect_after_login(auth_id)
    form = LoginForm()
    if form.validate_on_submit():
        try:
            data = auth.sign_in(
                email=form.email.data,
                password=form.password.data
            )
            access_token = data.session.access_token
            auth_id = data.user.id
        except Exception as e:
            flash(str(e))

        session["access_token"] = access_token
        redirect_str = redirect_after_login(auth_id)
        return redirect(url_for(redirect_str))
    
    return render_template("accounts/login.html", form=form)

@accounts_app.route("/logout", methods=["GET"])
@login_required
def logout_view():
    session.pop("user_details", None)
    session.pop("access_token", None)
    session.pop("_flashes", None)
    auth.sign_out()
    return redirect(url_for("accounts.login_view"))

@accounts_app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_view():
    DOMAIN = current_app.config["DOMAIN"]
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        auth.reset_password(email=email, domain=DOMAIN)
        flash(
            "An email with instructions to reset your password has been sent",
            "message"
        )
    return render_template("accounts/forgot-password.html", form=form)

@accounts_app.route("/reset-password", methods=["GET", "POST"])
def reset_password_view():
    access_token = request.args.get("access_token", "")
    if not access_token:
        return redirect(url_for("login_view"))
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data
        try:
            auth.update_user({
                "password": new_password
            })
            flash("Password successfully updated.", "message")
        except Exception:
            flash("There was a problem updating your password. "
                  "Please try again.",
                  "error"
            )
            
    return render_template("accounts/reset-password.html", form=form)

@accounts_app.route("/account", methods=["GET"])
@login_required
def account_view(section="profile"):
    account_form = AccountManagementForm()
    password_form = UpdatePasswordForm()
    buy_credits_form = BuyCreditsForm()
    binders_db = get_binders()

    return render_template(
        "accounts/account.html",
        section=section,
        account_form=account_form,
        password_form=password_form,
        binders_db=binders_db,
        buy_credits_form=buy_credits_form
    )

@accounts_app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_view():
    if request.method == "GET":
        return redirect(url_for("accounts.account_view", section="profile"))
    account_form = AccountManagementForm()
    password_form = UpdatePasswordForm()
    if account_form.validate_on_submit():
        form = account_form
        if form.email.data:
            new_email = form.email.data
            session["user_details"]["email"] = new_email
            try:
                data = auth.update_user(
                    {"email": new_email}
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
            flash("Your profile has been updated.", "message")
        else:
            flash("There was an error updating your profile.", "error")
        return redirect(url_for("accounts.account_view", section="profile"))
    
    if password_form.validate_on_submit():
        new_password = password_form.new_password.data
        try:
            response = auth.update_user(
                {"password":new_password}
            )
            access_token = response.access_token
            session["access_token"] = access_token
            flash("Password successfully updated.", "message")
        except Exception:
            flash(
                "There was a problem updating your password. "
                "Please try again.",
                "error"
            )
        return redirect(url_for("accounts.account_view", section="profile"))

@accounts_app.route("/view-binders", methods=["GET"])
@login_required
def view_binders_view():
    return redirect(url_for("accounts.account_view", section="view-binders"))

@accounts_app.route("/buy-credits", methods=["GET", "POST"])
@login_required
def buy_credits_view():
    if request.method == "GET":
        return redirect(
            url_for("accounts.account_view", section="buy-credits")
        )
    form = BuyCreditsForm()
    if form.validate_on_submit():
        num_credits = form.credits.data
        return redirect(url_for(
            "stripe.checkout_view",
            num_credits=num_credits
        ))
