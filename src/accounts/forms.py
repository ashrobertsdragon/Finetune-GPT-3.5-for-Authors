from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length

from src.accounts.models import UserTable

class SignupForm(FlaskForm):
    email = EmailField(
        "Email", validators=[DataRequired(), Email(message=None), Length(min=6, max=40)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    accept_tos = BooleanField('I accept the Terms of Service', validators=[DataRequired()])

    def validate(self):
        initial_validation = super(SignupForm, self).validate()
        if not initial_validation:
            return False
        user = UserTable.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])