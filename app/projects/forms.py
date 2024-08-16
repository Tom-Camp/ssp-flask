from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, TextAreaField
from wtforms.validators import DataRequired


class MaintainersForm(FlaskForm):
    maintainer = StringField()


class ProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    maintainers = FieldList(FormField(MaintainersForm), min_entries=1)
