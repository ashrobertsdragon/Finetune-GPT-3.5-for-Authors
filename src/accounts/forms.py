from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, TextField, DateField, SubmitField, IntegerRangeField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class SignupForm(FlaskForm):
    email = EmailField(
        "Email", validators=[
            DataRequired(),
            Email(message=None),
            Length(min=6, max=40)]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    terms_agreement = BooleanField(
        "I agree to the ",
        validators=[DataRequired()]
    )
    submit = SubmitField("Signup")

    def validate(self):
        initial_validation = super(SignupForm, self).validate()
        if not initial_validation:
            return False
        return True

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class AccountManagementForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[Email()], 
        filters=[lambda x: x or None]
    )
    first_name = TextField("First name",
        filters=[lambda x: x or None]
    )
    last_name = TextField("Last name",
        filters=[lambda x: x or None]
    )
    b_day = DateField("Birthdate",
        filters=[lambda x: x or None]
    )
    submit_account = SubmitField("Update Account")

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField("Password", validators=[DataRequired()])
    new_password = PasswordField("Password", validators=[DataRequired()])
    submit_password = SubmitField("Update Password")

class BuyCreditsForm(FlaskForm):
    credits = IntegerRangeField(
        "Credits",
        validators=[
            DataRequired(),
            NumberRange(min=1,max=10)
        ]
    )
    submit = SubmitField("Buy Credits")