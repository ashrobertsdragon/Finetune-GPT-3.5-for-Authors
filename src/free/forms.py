from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp

class EbookConversionForm(FlaskForm):
    ebook = FileField("Upload ebook", validators=[
        DataRequired(),
        FileAllowed(["pdf", "epub", "docx", "txt"], "Unsupported file type")
    ])
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    rights_confirmation = BooleanField(
        "I confirm that I have the rights to these files",
        validators=[DataRequired()]
    )
    terms_agreement = BooleanField(
        "I agree to the ",
        validators=[DataRequired()]
    )
    submit = SubmitField("Convert")
    
class FineTuneForm(FlaskForm):
    user_key = StringField("OpenAI API key", validators=[
        DataRequired(), 
        Regexp("^sk-", message="Key must start with 'sk-'"),
        Length(
            min=51,
            max=59,
            message="Key length must be between 50 and 60 characters"
        )
    ])
    file = FileField("Upload Text File(s)", validators=[
        DataRequired(),
        FileAllowed(["txt", "text"], "Text files only!")
    ])
    role = TextAreaField("System message", validators=[DataRequired()])
    chunk_type = SelectField("Fine tuning method", choices=[
        ("placeholder", "Choose one"),
        ("sliding_window_small", "Sliding Window (chapter-level)"),
        ("sliding_window_large", "Sliding Window (book-level)"),
        ("dialogue_prose", "Dialogue/Prose"),
        ("generate_beats", "Generate Beats (extra cost)")
    ], validators=[DataRequired()])
    rights_confirmation = BooleanField(
        "I confirm that I have the rights to these files",
        validators=[DataRequired()]
    )
    terms_agreement = BooleanField(
        "I agree to the ",
        validators=[DataRequired()]
    )
    submit = SubmitField("Finetune GPT-3.5")