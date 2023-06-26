from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    password = PasswordField(_l('Password'), validators=[DataRequired()])
