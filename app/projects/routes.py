from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, request

from app.projects.forms import ProjectForm
from app.projects.models import Project
from app.projects.views import get_projects
from app.utils.helpers import load_yaml, write_yaml
from app.utils.library import Library

project_bp = Blueprint("project", __name__, url_prefix="/project")


def get_destination_path(file: str) -> str:
    """
    Given a library path and a Project machine_name, return a file path to use
    to copy the library file into the Project.

    :param file: str - the library file path
    :return: str - the file path in the Project directory
    """
    return "/".join(Path(file).parts[1:])


def project_add_files(project_name: str, file_list: list) -> list:
    """
    Give a list of library files, add them to a Project.

    :param project_name: str the Project machine_name
    :param file_list: a list of library file paths as strings
    :return: a list of Project file paths as strings
    """
    files: list = []
    library = Library(project_machine_name=project_name)
    for file in file_list:
        files.append(library.copy(filepath=file))
    return files


def project_remove_files(project_name: str, file_list: list) -> list:
    """
    Give a list of library files, remove them to a Project.

    :param project_name: str the Project machine_name
    :param file_list: a list of library file paths as strings
    :return: a list of Project file paths as strings
    """
    files: list = []
    library = Library(project_machine_name=project_name)
    for file in file_list:
        library.remove(
            filepath=file,
        )
        files.append(file)
    return files


def load_project(project_name: str) -> Project:
    """
    Return a Project object.

    :param project_name: str the Project machine_name
    :return: Project
    """
    project_file = load_yaml(
        Path("project_data")
        .joinpath(project_name)
        .joinpath("project")
        .with_suffix(".yaml")
        .as_posix()
    )
    # Need to fix this.
    if project_file:
        project = Project(**project_file)
    else:
        project = Project()
    return project


@project_bp.route("/list", methods=["GET"])
def project_list_page():
    """
    A page to list all the Projects.

    :return: HTML template
    """
    projects = get_projects()
    return render_template("project/project_list.html", projects=projects)


@project_bp.route("/create", methods=["GET", "POST"])
def project_create_page():
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
                maintainers=[name.get("maintainer") for name in form.maintainers.data],
                project_dir=None,
                opencontrol=None,
                machine_name=None,
            )
            project.create()
            return redirect("/project/list")

    return render_template("project/project_form.html", form=form)


@project_bp.route("/<project_name>", methods=["GET"])
def project_view_page(project_name: str):
    """
    A view of an individual Project.

    :param project_name: str - machine_name for the Project.
    :return: HTML template
    """
    project = load_project(project_name=project_name)
    page: dict = project.view()
    return render_template("project/project.html", **page)


@project_bp.route("/<project_name>/add/<directory>", methods=["GET", "POST"])
def project_files_add_page(project_name: str, directory: str):
    """
    A page to add OpenControl certifications and standards.

    :param project_name: str - machine_name for the Project.
    :param directory: str - either standards or certifications
    :return: HTML template
    """
    source = directory.lower()
    library = Library(project_machine_name=project_name)
    directories = library.list_directories()

    if source not in directories:
        abort(404)

    files = library.list_files(directory=source)
    project = load_project(project_name)

    data: dict = {
        "project_name": project_name,
        "name": project.name,
        "file_list": files,
        "project_files": project.get_project_files_by_directory(directory=directory),
    }

    # if request.method == "POST":
    #     file_list: list = [file for file in request.form.getlist("files")]
    #     new_files = project_add_files(project_name=project_name, file_list=file_list)
    #     opencontrol_file[oc_key] = new_files
    #     write_yaml(
    #         filename=opencontrol.as_posix(),
    #         data=opencontrol_file,
    #     )

    return render_template("project/project_add_files_form.html", **data)


@project_bp.route("/<project_name>/delete/<filetype>/<filename>", methods=["GET"])
def project_files_delete_page(project_name: str, filetype: str, filename: str):
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
