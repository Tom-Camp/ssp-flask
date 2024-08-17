from pathlib import Path

from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, TextAreaField, ValidationError
from wtforms.validators import DataRequired

from app.utils.helpers import get_machine_name


def project_name_validation(form, field):
    name = get_machine_name(name=field.data)
    if any(project.name == name for project in Path("project_data").glob("*")):
        raise ValidationError(f"{field.data} project exists.")


class MaintainersForm(FlaskForm):
    maintainer = StringField()


class ProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), project_name_validation])
    description = TextAreaField("Description", validators=[DataRequired()])
    maintainers = FieldList(FormField(MaintainersForm), min_entries=1)
