from pathlib import Path

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.projects.forms import ProjectForm
from app.projects.models import Project
from app.projects.views import get_project_data, get_projects

project_bp = Blueprint("project", __name__, url_prefix="/project")


@project_bp.route("/list", methods=["GET"])
def project_list_view():
    """
    A page to list all the Projects.

    :return: HTML template
    """
    projects = get_projects()
    if not projects:
        project_create_url = url_for("project.project_create_page")
        flash(
            message=(
                f"There are no projects in the /project_data directory.<br>"
                f'<a href="{project_create_url}">Click here to a new Project</a>.'
            ),
            category="info",
        )
    return render_template("project/project_list_view.html", projects=projects)


@project_bp.route("/create", methods=["GET", "POST"])
def project_create_view():
    """
    A page to create an SSP Toolkit Project

    :return: HTML template
    """
    form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            project = Project(
                name=form.name.data,
                description=form.description.data,
            )
            project.create()
            return redirect(
                url_for("project.project_view", project_name=project.machine_name)
            )

    return render_template("project/project_create_view.html", form=form)


@project_bp.route("/<project_name>", methods=["GET"])
def project_view(project_name: str):
    """
    A view of an individual Project.

    :param project_name: str - machine_name for the Project.
    :return: HTML template
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)
    if not project_path.exists():
        abort(404)

    _, project, _, opencontrol = get_project_data(project_name)
    todo: list = []
    for section in ["components", "certifications", "standards"]:
        if not getattr(opencontrol, section):
            if section == "opencontrol":
                url: str = url_for(
                    "opencontrol.components_add_list_view", project_name=project_name
                )
            else:
                url = "#"
            todo.append(
                f"<a class='text-white' href='{url}'>Click here to add {section}</a>"
            )

    data: dict = {
        "project": project,
        "todo": todo,
    }

    return render_template("project/project_view.html", **data)


@project_bp.route("/<project_name>/templates/<directory>", methods=["GET"])
def project_templates_view(project_name: str, directory: str):
    """
    A page to add templates to a Project.

    :param project_name: str - machine_name for the Project.
    :param directory: str - the template directory name.
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)
    allowed_directories = ["appendices", "frontmatter", "tailoring"]
    if not project_path.exists() or directory not in allowed_directories:
        abort(404)

    project_templates = manager.get_files_by_directory(directory)

    data: dict = {
        "directory": directory,
        "project": project,
        "templates": project_templates,
    }
    return render_template("project/project_templates.html", **data)


@project_bp.route("/<project_name>/files/add/<directory>", methods=["GET"])
def project_files_add_view(project_name: str, directory: str):
    """
    A page to add OpenControl certifications and standards.

    :param project_name: str - machine_name for the Project.
    :param directory: str - either standards or certifications
    :return: HTML template
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)
    allowed_directories = ["appendices", "opencontrol", "frontmatter", "tailoring"]
    if not project_path.exists() or directory not in allowed_directories:
        abort(404)

    project_templates = manager.get_files_by_directory(directory)
    library_templates = project.library.list_files(
        directory=Path("templates").joinpath(directory).as_posix()
    )
    new_templates: list = [
        file for file in library_templates if file not in project_templates
    ]

    data: dict = {
        "directory": directory,
        "project": project,
        "project_templates": project_templates,
        "templates": new_templates,
    }

    return render_template("project/project_files_add_view.html", **data)


@project_bp.route("/<project_name>/file/add", methods=["POST"])
def project_files_add_submit(project_name: str):
    """
    Submit handler for adding template files.

    :param project_name: str - machine_name for the Project.
    :return: redirect to page that submitted the request
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)

    parents = request.form.get("parents")
    for file in request.form.getlist("files"):
        copy_path = f"templates/{parents}/{file}"
        destination = project_path.joinpath(copy_path)
        if project.library.library.joinpath(copy_path).is_dir():
            project.library.copy_directory(
                source_path=copy_path, destination_path=destination.as_posix()
            )
        else:
            project.library.copy_file(
                source_path=copy_path, destination_path=destination.as_posix()
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@project_bp.route("/<project_name>/file/remove", methods=["POST"])
def project_files_remove_submit(project_name: str):
    """
    Submit handler for removing template files.

    :param project_name: str - machine_name for the Project.
    :return: redirect to page that submitted the request
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)

    parents = request.form.get("parents")
    for file in request.form.getlist("files"):
        copy_path = f"templates/{parents}/{file}"
        manager.remove_file(source_path=copy_path)

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )
