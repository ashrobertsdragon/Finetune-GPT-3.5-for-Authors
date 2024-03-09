from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, TextField, DateField
from wtforms.validators import DataRequired, Email, Length

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
        return True

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class AccountManagementForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    current_password = PasswordField("Password", validators=[DataRequired()])
    new_password = PasswordField("Password", validators=[DataRequired()])
    first_name = TextField("First name")
    last_name = TextField("Last name")
    b_day = DateField("Birthdate")