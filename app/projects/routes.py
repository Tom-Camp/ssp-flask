from flask import Blueprint, redirect, render_template, request

from app.projects.forms import ProjectForm
from app.projects.models import Project

project_bp = Blueprint("project", __name__, url_prefix="/project")


@project_bp.route("/list", methods=["GET"])
def projects_list():
    return render_template("project/projects.html")


@project_bp.route("/create", methods=["GET", "POST"])
def projects_create():
    form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            project = Project(
                name=form.name.data,
                description=form.description.data,
                maintainers=[name.get("maintainer") for name in form.maintainers.data],
                oc_file=None,
                config_file=None,
                certifications=None,
                standards=None,
                keys=None,
                project_dir=None,
            )
            project.create()
        return redirect("/project/list")

    return render_template("project/projects_form.html", form=form)


@project_bp.route("/project/<project_name>")
def project_view(project_name: str):
    """"""
    return render_template("project/projects.html", title=project_name)
