from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import HiddenField, SelectField, SelectMultipleField, widgets, TextAreaField


class CheckBoxGroup(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class WiFiFeedbackForm(FlaskForm):
    user = HiddenField(_l('User ID'))
    quality = SelectField(_l('My WiFi connection was'), coerce=int, choices=[
        (1, _l('Nowhere to be seen')),
        (2, _l('Poor')),
        (3, _l('Variable')),
        (4, _l('Good')),
        (5, _l('Perfect')),
    ])
    coverage = CheckBoxGroup(_l('The coverage should be improved here'), coerce=int, choices=[
        (1, _l('Camp')),
        (2, _l('Arena')),
        (3, _l('Sanitary facilities')),
        (4, _l('Infopoint')),
        (5, _l('Stations besides camp')),
        (6, _l('Stations behind the forest')),
    ])
    further_notes = TextAreaField(_l('Further notes'), render_kw={'rows': 5})


class WebsiteFeedbackForm(FlaskForm):
    user = HiddenField(_l('User ID'))
    keep = TextAreaField(_l('Keep this'))
    remove = TextAreaField(_l('Remove this'))
    add = TextAreaField(_l('Add this'))
    further_notes = TextAreaField(_l('Further notes'), render_kw={'rows': 5})