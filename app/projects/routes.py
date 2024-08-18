from pathlib import Path

from flask import Blueprint, redirect, render_template, request

from app.projects.forms import ProjectForm
from app.projects.models import Project
from app.utils.helpers import load_yaml, write_yaml
from app.utils.library import Library

project_bp = Blueprint("project", __name__, url_prefix="/project")


def get_destination_path(file: str) -> str:
    return Path(*Path(file).parts[1:]).as_posix()


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
        page = project.load()
    return render_template("project/project.html", data=page)


@project_bp.route("/<project_name>/add/standards", methods=["GET", "POST"])
def project_add_standards(project_name: str):
    project_path = Path("project_data").joinpath(project_name)
    opencontrol = project_path.joinpath("opencontrol").with_suffix(".yaml")

    opencontrol_file = load_yaml(opencontrol.as_posix())
    oc_standards: list = [
        Path(standard).name for standard in opencontrol_file.get("standards", [])
    ]
    library = Library(project_path=project_path.as_posix())
    files = Library(project_path=project_path.as_posix()).list_files(
        dirname="standards"
    )
    data: dict = {
        "filename": "opencontrol.yaml standards",
        "project_name": project_name,
        "file_list": files,
        "standards": oc_standards,
    }

    if request.method == "POST":
        for file in request.form.getlist("files"):
            filename = get_destination_path(file)
            destination = filename
            library.copy(
                filename=filename,
                dest=destination,
            )
            opencontrol_file["standards"].append(destination)
            write_yaml(
                filename=opencontrol.as_posix(),
                data=opencontrol_file,
            )
    return render_template("project/project_add_files_form.html", **data)


@project_bp.route("/<project_name>/delete/standards/<filename>", methods=["GET"])
def project_delete_standards(project_name: str, filename: str):
    opencontrol = (
        Path("project_data")
        .joinpath(project_name)
        .joinpath("opencontrol")
        .with_suffix(".yaml")
    )
    opencontrol_file = load_yaml(opencontrol.as_posix())
    oc_standards: dict = {
        Path(standard).name: Path(standard).as_posix()
        for standard in opencontrol_file.get("standards", [])
    }
    library = Library(
        project_path=Path("project_data").joinpath(project_name).as_posix()
    )
    library.remove(filename=oc_standards[filename])
    opencontrol_file["standards"].remove(oc_standards[filename])
    write_yaml(filename=opencontrol.as_posix(), data=opencontrol_file)
    return redirect(f"/project/{project_name}/add/standards")
