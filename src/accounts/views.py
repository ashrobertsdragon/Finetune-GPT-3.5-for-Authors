from flask import Blueprint, render_template, redirect, jsonify, session


from src import app
from src.supabase_client import supabase
from .forms import SignupForm, LoginForm
from .utils import create_user, login_required

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
            create_user(user_id)
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
    session.pop('access_token', None)
    supabase.auth.sign_out()
    return redirect("/login.html")