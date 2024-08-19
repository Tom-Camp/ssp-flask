from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, request

from app.projects.forms import ProjectForm
from app.projects.models import Project
from app.projects.views import get_projects
from app.utils.helpers import load_yaml, write_yaml
from app.utils.library import Library

project_bp = Blueprint("project", __name__, url_prefix="/project")


def get_destination_path(file: str) -> str:
    return Path(*Path(file).parts[1:]).as_posix()


@project_bp.route("/list", methods=["GET"])
def projects_list():
    projects = get_projects()
    return render_template("project/projects.html", projects=projects)


@project_bp.route("/create", methods=["GET", "POST"])
def projects_create():
    form = ProjectForm()
    if request.method == "POST":
        if form.validate_on_submit():
            project = Project(
                name=form.name.data,
                description=form.description.data,
                maintainers=[name.get("maintainer") for name in form.maintainers.data],
                project_dir="",
            )
            project.create()
            return redirect("/project/list")

    return render_template("project/projects_form.html", form=form)


@project_bp.route("/<project_name>", methods=["GET"])
def project_view(project_name: str):
    page: dict = {}
    project_file = load_yaml(
        Path("project_data")
        .joinpath(project_name)
        .joinpath("project")
        .with_suffix(".yaml")
        .as_posix()
    )
    if project_file:
        project = Project(**project_file)
        page = {"appendices": project.get_appendices(), "data": project.load()}
    return render_template("project/project.html", **page)


@project_bp.route("/<project_name>/add/<filetype>", methods=["GET", "POST"])
def project_add_oc_files(project_name: str, filetype: str):
    oc_key = filetype.lower()
    if oc_key not in ["standards", "certifications"]:
        abort(404)

    project_path = Path("project_data").joinpath(project_name)
    opencontrol = project_path.joinpath("opencontrol").with_suffix(".yaml")

    opencontrol_file = load_yaml(opencontrol.as_posix())
    oc_files: list = [
        Path(oc_file).name for oc_file in opencontrol_file.get(oc_key, [])
    ]
    library = Library(project_path=project_path.as_posix())
    files = Library(project_path=project_path.as_posix()).list_files(dirname=oc_key)
    data: dict = {
        "filename": f"opencontrol.yaml {oc_key}",
        "project_name": project_name,
        "file_list": files,
        "oc_files": oc_files,
    }

    if request.method == "POST":
        for file in request.form.getlist("files"):
            filename = get_destination_path(file)
            destination = filename
            library.copy(
                filename=filename,
                dest=destination,
            )
            opencontrol_file[oc_key].append(destination)
            write_yaml(
                filename=opencontrol.as_posix(),
                data=opencontrol_file,
            )
    return render_template("project/project_add_files_form.html", **data)


@project_bp.route("/<project_name>/delete/<filetype>/<filename>", methods=["GET"])
def project_delete_oc_files(project_name: str, filetype: str, filename: str):
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
    library = Library(
        project_path=Path("project_data").joinpath(project_name).as_posix()
    )
    library.remove(filename=oc_files[filename])
    opencontrol_file["standards"].remove(oc_files[filename])
    write_yaml(filename=opencontrol.as_posix(), data=opencontrol_file)
    return redirect(f"/project/{project_name}/add/{oc_key}")


@project_bp.route("/<project_name>/add/appendices", methods=["GET", "POST"])
def project_add_all_appendices(project_name: str):
    library = Library(
        project_path=Path("project_data").joinpath(project_name).as_posix()
    )
    library.copy_dir(
        directory="appendices",
        dest="templates/appendices",
    )
    return redirect(f"/project/{project_name}")
