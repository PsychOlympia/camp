from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField


class AddPointsForm(FlaskForm):
    team = SelectField()
    points = IntegerField()
    round = IntegerField()
