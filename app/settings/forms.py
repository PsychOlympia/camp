from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import HiddenField, FloatField
from wtforms.validators import DataRequired, NumberRange
from flask_babel import lazy_gettext as _l
from wtforms.widgets import HiddenInput


class HiddenFloatField(FloatField):
    widget = HiddenInput()


class MapLocationForm(FlaskForm):
    item_type = HiddenField('type', validators=[DataRequired()])
    item_name = HiddenField('name', validators=[DataRequired()])
    latitude = HiddenFloatField('latitude', validators=[DataRequired(), NumberRange(min=-90, max=90)])
    longitude = HiddenFloatField('longitude', validators=[DataRequired(), NumberRange(min=-180, max=180)])


class FileUploadForm(FlaskForm):
    file = FileField(_l('Upload file'), validators=[
        FileRequired(),
        FileAllowed(['jpeg', 'jpg', 'png', 'heic', 'webp'], _l('Only images are allowed!'))
    ])
