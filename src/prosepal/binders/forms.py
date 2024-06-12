from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import (
    BooleanField,
    FileField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


def csv_to_list(string: str) -> list:
    return string.split(",") if string else []


class LoreBinderForm(FlaskForm):
    author = StringField(
        "Author Name",
        validators=[Length(max=30), DataRequired()],
        description="Please enter author name or pen name for book",
        render_kw={"aria-label": "Author name for manuscript"},
    )
    title = StringField(
        "Book Title",
        validators=[Length(max=50), DataRequired()],
        description="Please enter title",
        render_kw={"aria-label": "Book title"},
    )
    is_first_person = BooleanField(
        "First Person Narrative",
        description=(
            "Please click if the manuscript is " "written in the first person"
        ),
        render_kw={
            "aria-label": "Choose if manuscript is written in first person"
        },
    )
    narrator = StringField(
        "Narrator Name",
        validators=[Length(max=30), Optional()],
        filters=[lambda x: x or None],
        description=(
            "Please identify what other characters most "
            "commonly call that narrator"
        ),
        render_kw={"aria-label": "Narrator's name"},
    )

    character_attributes = TextAreaField(
        "Character Attributes",
        validators=[Optional()],
        description=(
            "Please enter any other character attributes you "
            "wish ProsePal to search for"
        ),
        render_kw={
            "autocomplete": "off",
            "aria-label": "Character attributes to include",
            "rows": "5",
        },
    )
    other_attributes = TextAreaField(
        "Other Attributes",
        validators=[Optional()],
        description=(
            "Please enter any other types of information "
            "you wish ProsePal to search for"
        ),
        render_kw={
            "autocomplete": "off",
            "aria-label": "Other attributes for ProsePal to search for",
            "rows": "5",
        },
    )

    file_upload = FileField(
        "Document",
        validators=[
            FileRequired(),
            FileAllowed(["docx", "epub", "pdf", "txt"], "Invalid file format"),
        ],
        description="Please upload your manuscript",
    )

    submit = SubmitField("Create LoreBinder")
