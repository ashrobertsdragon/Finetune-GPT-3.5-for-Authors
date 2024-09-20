from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import (
    BooleanField,
    DateField,
    EmailField,
    IntegerRangeField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
)


def value_or_none(form, field):
    return field.data or None


class SignupForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(min=6, max=40)],
        render_kw={"aria-label": "Email address", "autocomplete": "email"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, max=25)],
        render_kw={"aria-label": "Password", "autocomplete": "new-password"},
    )
    terms_agreement = BooleanField(
        Markup(
            "I agree to the <a href='/terms' target='_blank'>"
            "terms and conditions</a>"
        ),
        validators=[DataRequired()],
        render_kw={"aria-label": "Agree to terms and conditions"},
    )
    submit = SubmitField("Signup", render_kw={"aria-label": "Sign up"})

    def validate(self, extra_validators=None):
        initial_validation = super().validate(extra_validators)
        if not initial_validation:
            return False
        return True


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"aria-label": "Email address", "autocomplete": "email"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={
            "aria-label": "Password",
            "autocomplete": "current-password",
        },
    )
    submit = SubmitField("Login", render_kw={"aria-label": "Log in"})


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        Markup(
            "Enter the email address you signed up with<br \\>"
            "and you will receive a link to reset your<br \\>password"
        ),
        validators=[DataRequired(), Email()],
        render_kw={
            "aria-label": "Enter email address",
            "autocomplete": "email",
        },
    )
    submit = SubmitField(
        "Reset Password",
        render_kw={"aria-label": "Request reset password link"},
    )


class AccountManagementForm(FlaskForm):
    email = EmailField(
        "Email address:",
        validators=[DataRequired(), Email()],
        render_kw={
            "aria-label": "Update email address",
            "auto-complete": "email",
        },
    )
    first_name = StringField(
        "First name:",
        validators=[Optional()],
        render_kw={"aria-label": "First name", "autocomplete": "given-name"},
    )
    last_name = StringField(
        "Last name:",
        validators=[Optional()],
        render_kw={"aria-label": "First name", "autocomplete": "family-name"},
    )
    b_day = DateField(
        "Birthdate:",
        validators=[Optional()],
        render_kw={
            "aria-label": "Birthdate, format YYYY-MM-DD",
            "autocomplete": "bday",
        },
    )
    submit_account = SubmitField("Update Account")


class UpdatePasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password:",
        validators=[DataRequired()],
        render_kw={
            "aria-label": "New Password",
            "autocomplete": "new-password",
        },
    )
    submit_password = SubmitField(
        "Update Password", render_kw={"aria-label": "Update password"}
    )


class BuyCreditsForm(FlaskForm):
    credits = IntegerRangeField(
        "Credits:",
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        render_kw={"aria-label": "Credits to buy"},
        default=1,
    )
    submit = SubmitField(
        "Buy Credits", render_kw={"aria-label": "Buy credits"}
    )