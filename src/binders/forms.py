from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, FileField, HiddenField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired

class LoreBinderForm(FlaskForm):
    author = StringField(
        'Author Name',
        validators=[
            Length(max=30),
            DataRequired()
        ],
        render_kw={"aria-label": "Author name for manuscript"}
    )
    title = StringField(
        'Book Title',
        validators=[
            Length(max=50),
            DataRequired()
            ],
            render_kw={"aria-label": "Book title"}
    )
    is_first_person = BooleanField(
        'First Person Narrative',
        render_kw={"aria-label": "Choose first or third person for manuscript"}
    )
    narrator = StringField(
        'Narrator Name',
        validators=[Length(max=30)],
        render_kw={"aria-label": "Narrator's name"},
        filters=[lambda x: x or None]
    )
    
    character_attributes_input = StringField(
        'Character Attributes',
        render_kw={
            "autocomplete": "off",
            "aria-label": "Character attributes to include"
        },
        filters=[lambda x: x or None]
        )
    other_attributes_input = StringField(
        'Other Attributes',
        render_kw={
            "autocomplete": "off",
            "aria-label": "Other attributes for AI to search for"
        },
        filters=[lambda x: x or None]
    )
    
    character_attributes = HiddenField(filters=[lambda x: x or None])
    other_attributes = HiddenField(filters=[lambda x: x or None])

    file_upload = FileField('Document', validators=[
        FileRequired(),
        FileAllowed(['docx', 'epub', 'pdf', 'txt'], 'Invalid file format')])
