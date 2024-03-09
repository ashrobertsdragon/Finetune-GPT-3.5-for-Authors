from flask import Blueprint, render_template, redirect, jsonify, session, url_for, flash


from src import app
from src.supabase_client import supabase
from src.utils import login_required
from .forms import SignupForm, LoginForm, AccountManagementForm, UpdatePasswordForm
from .utils import add_user_prefix

accounts_bp = Blueprint("accounts", __name__)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        res = supabase.auth.sign_up({
            "email": form.email.data,
            "password": form.password.data,
        })
        if res.error:
            return jsonify({"error": {res.error.message}}), res.error.status
        else:
            user_id  = res.data["user"].get("id")
            add_user_prefix(user_id)
            return jsonify({"success": True, "message": "Signup successful. Please check your email to verify your account."}), 200
    
    return render_template("signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = supabase.auth.sign_in_with_password({
            "email": form.email.data,
            "password": form.password.data
        })
        if data.error:
            return jsonify({"error": {data.error.message}}), data.error.status
        
        access_token = data.data.access_token
        session["access_token"] = access_token

        user_id = data.user.id
        query = supabase.from_("userTable").select("credits_available").eq("uuid", user_id)
        response = query.execute()
        credits_available = response.data[0]["credits_available"]
        if credits_available > 0:
            return redirect("lorebinder.html")
        else:
            return redirect("account.html#but_credits")
    return render_template("login.html", form=form)

@app.route("/logout", method=["GET"])
@login_required
def logout():
    session.pop("access_token", None)
    supabase.auth.sign_out()
    return redirect("/login.html")

@app.route("/account")
@login_required
def account_view():
    user_id = session.get("user_id")
    error, data = supabase.table("userTable").select("*").eq("id", user_id).single().execute()
    if not error and data:
        user_dict = {}
        user_dict["email"] = data.get("email", "")
        user_dict["first_name"] = data.get("first_name", "")
        user_dict["last_name"] = data.get("last_name", "")
        user_dict["form.b_day"] = data.get("b_day", None)
        user_dict["credits_available"]  = data.get("credits_available")
        user_dict["credits_used"] = data.get("credits_used")
    


    if section == "profile":
        return profile()
    elif section == "view_binders":
        return view_binders()
    elif section == "buy_credits":
        return buy_credits()
    else:
        return redirect(url_for("account_view", section="profile"))
    
@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    account_form = AccountManagementForm()
    password_form = UpdatePasswordForm()
    if account_form.validate_on_submit():
        form = account_form
        update_user = {}
        if form.email.data:
            update_user["email"] = form.email.data
        if form.first_name.data:
            update_user["f_name"] = form.first_name.data
        if form.last_name.data:
            update_user["l_name"] = form.last_name.data
        if form.b_day.data:
            update_user["b_day"] = form.b_day.data
        if update_user:
            error, _ = supabase.table("userTable").update(update_user).eq("id", user_id).execute()

            if error:
                flash("There was an error updating your profile.", "error")
            else:
                flash("Your profile has been updated.", "success")

        return redirect(url_for("account_view", section="profile"))
    
    if password_form.validate_on_submit():
        new_password = password_form.new_password.data
        error = supabase.auth.update_user(
            access_token=session['access_token'],
            password=new_password
        )

        if error:
            flash("There was a problem updating your password. Please try again.", "error")
        else:
            flash("Password successfully updated.", "success")

    return render_template("profile.html", account_form=account_form, password_form=password_form)

