from pathlib import Path

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.projects.forms import ProjectForm
from app.projects.models import Project
from app.projects.views import get_project_request_defaults, get_projects, load_project
from app.utils.helpers import load_yaml, write_yaml

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
            category="is-info",
        )
    return render_template("project/project_list.html", projects=projects)


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

    return render_template("project/project_form.html", form=form)


@project_bp.route("/<project_name>", methods=["GET"])
def project_view(project_name: str):
    """
    A view of an individual Project.

    :param project_name: str - machine_name for the Project.
    :return: HTML template
    """
    project_path, project = get_project_request_defaults(project_name)
    if not project_path.exists():
        abort(404)

    project = load_project(project_name=project_name)
    return render_template("project/project.html", project=project.model_dump())


@project_bp.route("/<project_name>/templates/<directory>", methods=["GET"])
def project_templates_view(project_name: str, directory: str):
    """
    A page to add templates to a Project.

    :param project_name: str - machine_name for the Project.
    :param directory: str - the template directory name.
    """
    project_path, project = get_project_request_defaults(project_name)
    allowed_directories = ["appendices", "frontmatter", "tailoring"]
    if not project_path.exists() or directory not in allowed_directories:
        abort(404)

    project_templates = project.get_project_files_by_directory(f"templates/{directory}")

    data: dict = {
        "directory": directory,
        "project": project,
        "templates": project_templates,
    }
    return render_template("project/project_templates.html", **data)


@project_bp.route("/<project_name>/templates/add/<directory>", methods=["GET", "POST"])
def project_templates_add_view(project_name: str, directory: str):
    """
    A page to add OpenControl certifications and standards.

    :param project_name: str - machine_name for the Project.
    :param directory: str - either standards or certifications
    :return: HTML template
    """
    project_path, project = get_project_request_defaults(project_name)
    allowed_directories = ["appendices", "frontmatter", "tailoring"]
    if not project_path.exists() or directory not in allowed_directories:
        abort(404)

    if request.method == "POST":
        for file in request.form.getlist("files[]"):
            copy_path = f"templates/{file}"
            destination = project_path.joinpath("templates").joinpath(file)
            if project.library.library.joinpath(copy_path).is_dir():
                project.library.copy_directory(
                    copy_path, destination_path=destination.as_posix()
                )
            else:
                project.library.copy_file(
                    source_path=copy_path, destination_path=destination.as_posix()
                )
        return redirect(
            url_for(
                "project.project_templates_view",
                project_name=project_name,
                directory=directory,
            )
        )

    project_templates = project.get_project_files_by_directory(f"templates/{directory}")
    library_templates = project.library.list_files(
        directory=Path("templates").joinpath(directory).as_posix()
    )
    new_templates: list = []
    for file in library_templates:
        if file not in project_templates:
            new_templates.append(file)

    data: dict = {
        "directory": directory,
        "project": project,
        "templates": new_templates,
    }

    return render_template("project/project_templates_add.html", **data)


@project_bp.route("/<project_name>/delete/<filetype>/<filename>", methods=["GET"])
def project_files_delete_view(project_name: str, filetype: str, filename: str):
    """
    A page to remove OpenControl certifications and standards.

    :param project_name: str - machine_name for the Project.
    :param filetype: str - either standards or certifications
    :param filename: str - the filename to remove
    :return: HTML template
    """
    oc_key = filetype.lower()
    if oc_key not in ["standards", "certifications"]:
        abort(404)

    opencontrol = (
        Path("project_data")
        .joinpath(project_name)
        .joinpath("opencontrol")
        .with_suffix(".yaml")
    )
    opencontrol_file = load_yaml(opencontrol.as_posix())
    oc_files: dict = {
        Path(oc_file).name: Path(oc_file).as_posix()
        for oc_file in opencontrol_file.get(oc_key, [])
    }
    opencontrol_file["standards"].remove(oc_files[filename])
    write_yaml(filename=opencontrol.as_posix(), data=opencontrol_file)
    return redirect(f"/project/{project_name}/add/{oc_key}")
