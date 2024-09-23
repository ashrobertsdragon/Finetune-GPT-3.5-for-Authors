from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Regexp

from .utils import ChunkType


class JSONLConversionForm(FlaskForm):
    file = FileField(
        "Upload CSV File(s)",
        validators=[
            DataRequired(),
            FileAllowed(["csv"], "CSV files only"),
        ],
    )
    submit = SubmitField("Convert to JSONL")


class EbookConversionForm(FlaskForm):
    ebook = FileField(
        "Upload ebook",
        validators=[
            DataRequired(),
            FileAllowed(
                ["pdf", "epub", "docx", "txt"], "Unsupported file type"
            ),
        ],
    )
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    rights_confirmation = BooleanField(
        "I confirm that I have the rights to these files",
        validators=[DataRequired()],
    )
    terms_agreement = BooleanField(
        "I agree to the ", validators=[DataRequired()]
    )
    submit = SubmitField("Convert")


class FineTuneForm(FlaskForm):
    user_key = PasswordField(
        "OpenAI API key",
        validators=[
            DataRequired(),
            Regexp("^sk-", message="Key must start with 'sk-'"),
            Length(
                min=51,
                max=59,
                message="Key length must be between 50 and 60 characters",
            ),
        ],
    )
    file = FileField(
        "Upload Text File(s)",
        validators=[
            DataRequired(),
            FileAllowed(["txt", "text"], "Text files only"),
        ],
    )
    role = TextAreaField("System message", validators=[DataRequired()])
    chunk_type = SelectField(
        "Fine tuning method",
        choices=[
            ("placeholder", "Choose one"),
            (ChunkType.SLIDING_WINDOW_SMALL, "Sliding Window (chapter-level)"),
            (ChunkType.SLIDING_WINDOW_SMALL, "Sliding Window (book-level)"),
            (ChunkType.DIALOG_PROSE, "Dialogue/Prose"),
            (ChunkType.GENERATE_BEATS, "Generate Beats (extra cost)"),
        ],
        validators=[DataRequired()],
    )
    rights_confirmation = BooleanField(
        "I confirm that I have the rights to these files",
        validators=[DataRequired()],
    )
    terms_agreement = BooleanField(
        "I agree to the ", validators=[DataRequired()]
    )
    submit = SubmitField("Finetune GPT-3.5")
