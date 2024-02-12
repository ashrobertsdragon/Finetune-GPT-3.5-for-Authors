from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
  name = StringField('Your Name', validators=[DataRequired()])
  email = StringField('Your Email', validators=[DataRequired(), Email()])
  message = TextAreaField('Your Message', validators=[DataRequired()])
  submit = SubmitField('Send Message')

class EbookConversionForm(FlaskForm):
  ebook = FileField('Upload ebook', validators=[
    DataRequired(),
    FileAllowed(['pdf', 'epub', 'docx', 'txt'], 'Unsupported file type')
  ])
  title = StringField('Title', validators=[DataRequired()])
  author = StringField('Author', validators=[DataRequired()])
  rights_confirmation = BooleanField('I confirm that I have the rights to these files', validators=[DataRequired()])
  terms_agreement = BooleanField('I agree to the ', validators=[DataRequired()])
  submit = SubmitField('Convert')
  