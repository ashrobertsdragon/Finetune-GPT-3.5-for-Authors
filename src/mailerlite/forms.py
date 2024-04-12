from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class WaitListSignupForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(min=6, max=40)],
        render_kw={"aria-label": "Email address", "autocomplete": "email"}
    )
    submit = SubmitField("Join Waitlist", render_kw={"aria-label": "Join Waitlist"})

class MailerLiteSignupForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(min=6, max=40)],
        render_kw={"aria-label": "Email address", "autocomplete": "email"}
    )
    ubmit = SubmitField("Subscribe", render_kw={"aria-label": "Subscribe"})