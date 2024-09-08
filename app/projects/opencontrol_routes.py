from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, request, url_for

from app.projects.views import get_project_data

opencontrol_bp = Blueprint("opencontrol", __name__, url_prefix="/project")


@opencontrol_bp.route("/<project_name>/opencontrol", methods=["GET"])
def opencontrol_view(project_name: str):
    """
    Returns a list of Components available to add to a Project.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)

    data: dict = {
        "project": project,
        "opencontrol": opencontrol.model_dump(),
    }

    return render_template("opencontrol/opencontrol_view.html", **data)


@opencontrol_bp.route("/<project_name>/templates/components", methods=["GET"])
def component_template_list_view(project_name: str):
    """
    Returns a list of Components available to add to a Project.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)

    data: dict = {
        "project": project,
        "components": opencontrol.components,
    }

    return render_template("opencontrol/components_templates_view.html", **data)


@opencontrol_bp.route("/<project_name>/<key>/add", methods=["GET"])
def components_add_list_view(project_name: str, key: str):
    """
    A view for list Components from the library.

    :param project_name: str - Project machine_name
    :param key: str - The OpenControl parameter
    :return: HTML template
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)
    if hasattr(opencontrol, key):
        section = getattr(opencontrol, key)
    else:
        abort(404)

    if key == "components":
        files = project.library.list_directories(directory="templates/components")
    else:
        files = project.library.list_files(key)

    project_files = [Path(file).name for file in section]
    file_root = Path("rendered_files/components") if key == "components" else Path()
    available_files: list = [
        file for file in files if file_root.joinpath(file) not in section
    ]
    data: dict = {
        "project": project,
        "available_files": available_files,
        "project_files": project_files,
        "key": key,
    }
    return render_template("opencontrol/components_templates_edit_view.html", **data)


@opencontrol_bp.route("<project_name>/opencontrol/add", methods=["POST"])
def opencontrol_add_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    key = request.form.get("key")
    path = (
        Path(key) if key != "components" else Path("templates").joinpath("components")
    )
    for filename in request.form.getlist("files"):
        copy_path = path.joinpath(filename)
        destination = project_path.joinpath(copy_path)
        if project.library.library.joinpath(copy_path).is_dir():
            project.library.copy_directory(
                source_path=copy_path.as_posix(),
                destination_path=destination.as_posix(),
            )
        section = getattr(opencontrol, key)
        if filename not in section:

            opencontrol.update(
                project_path=project_path.as_posix(),
                key=key,
                action="add",
                attribute=(
                    f"rendered_files/components/{filename}"
                    if key == "components"
                    else key
                ),
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/opencontrol/remove", methods=["POST"])
def opencontrol_remove_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    key = request.form.get("key")
    path = (
        project_path.joinpath(key)
        if key != "components"
        else project_path.joinpath("templates").joinpath("components")
    )
    for filename in request.form.getlist("files"):
        remove_file = path.joinpath(filename)
        if remove_file.is_file():
            manager.remove_file(source_path=remove_file.as_posix())
        elif remove_file.is_dir():
            manager.remove_directory(
                source=remove_file.as_posix(),
                destination=project_path.joinpath("trash").as_posix(),
            )
        section = getattr(opencontrol, key)
        remove_path = (
            Path("rendered_files/components").joinpath(filename)
            if key == "components"
            else Path(filename)
        )
        if remove_path.as_posix() in section:
            opencontrol.update(
                project_path=project_path.as_posix(),
                key=key,
                action="remove",
                attribute=remove_path.as_posix(),
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )
