from flask import Markup
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, TextField, DateField, SubmitField, IntegerRangeField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class SignupForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(min=6, max=40)],
        render_kw={"aria-label": "Email address"}
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, max=25)],
        render_kw={"aria-label": "Password"}
    )
    terms_agreement = BooleanField(
        Markup("I agree to the <a href='/terms' target='_blank'>terms and conditions</a>"),
        validators=[DataRequired()],
        render_kw={"aria-label": "Agree to terms and conditions"}
    )
    submit = SubmitField("Signup", render_kw={"aria-label": "Sign up"})

    def validate(self):
        initial_validation = super(SignupForm, self).validate()
        if not initial_validation:
            return False
        return True

class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"aria-label": "Email address"}
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"aria-label": "Password"}
    )
    submit = SubmitField("Login", render_kw={"aria-label": "Log in"})


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[Email()], 
        render_kw={"aria-label": "Enter email address"}
    )
    submit = SubmitField("Reset Password", render_kw={"aria-label": "Request reset password link"})


class AccountManagementForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[Email()], 
        render_kw={"aria-label": "Update email address"},
        filters=[lambda x: x or None]
    )
    first_name = TextField("First name",
        render_kw={"aria-label": "First name"},
        filters=[lambda x: x or None]
    )
    last_name = TextField("Last name",
        render_kw={"aria-label": "First name"},
        filters=[lambda x: x or None]
    )
    b_day = DateField(
        "Birthdate",
        filters=[lambda x: x or None],
        render_kw={"aria-label": "Birthdate, format YYYY-MM-DD"}
    )
    submit_account = SubmitField("Update Account")

class UpdatePasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired()],
        render_kw={"aria-label": "New Password"}
    )
    submit_password = SubmitField("Update Password", render_kw={"aria-label": "Update password"})

class BuyCreditsForm(FlaskForm):
    credits = IntegerRangeField(
        "Credits",
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        render_kw={"aria-label": "Credits to buy"}
    )
    submit = SubmitField("Buy Credits", render_kw={"aria-label": "Buy credits"})
