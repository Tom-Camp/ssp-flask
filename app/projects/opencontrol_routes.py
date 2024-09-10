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
def opencontrol_add_elements_view(project_name: str, key: str):
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
    file_root = "rendered_files/components" if key == "components" else key
    available_files: list = [
        file for file in files if f"{file_root}/{file}" not in section
    ]
    data: dict = {
        "project": project,
        "available_files": available_files,
        "project_files": project_files,
        "key": key,
    }
    return render_template("opencontrol/components_templates_edit_view.html", **data)


@opencontrol_bp.route("<project_name>/component/add", methods=["POST"])
def opencontrol_component_add_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    for filename in request.form.getlist("files"):
        copy_path = Path("templates/components").joinpath(filename)
        destination = project_path.joinpath(copy_path)
        if project.library.library.joinpath(copy_path).is_dir():
            project.library.copy_directory(
                source_path=copy_path.as_posix(),
                destination_path=destination.as_posix(),
            )

            opencontrol.add(
                project_path=project_path.as_posix(),
                key="components",
                attribute=f"rendered_files/components/{filename}",
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/component/remove", methods=["POST"])
def opencontrol_component_remove_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    for filename in request.form.getlist("files"):
        remove_path = Path("templates/components").joinpath(filename)
        if project_path.joinpath(remove_path).is_dir():
            manager.remove_directory(source=remove_path.as_posix())

            opencontrol.remove(
                project_path=project_path.as_posix(),
                key="components",
                attribute=f"rendered_files/components/{filename}",
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/opencontrol/add", methods=["POST"])
def opencontrol_file_add_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    key = request.form.get("key")
    if key not in ["certifications", "standards"]:
        abort(404)

    for filename in request.form.getlist("files"):
        copy_path = Path(key).joinpath(filename)
        destination = project_path.joinpath(copy_path)
        if project.library.library.joinpath(copy_path).is_file():
            project.library.copy_file(
                source_path=copy_path.as_posix(),
                destination_path=destination.as_posix(),
            )

            opencontrol.add(
                project_path=project_path.as_posix(),
                key=key,
                attribute=f"{key}/{filename}",
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/opencontrol/remove", methods=["POST"])
def opencontrol_file_remove_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    key = request.form.get("key")
    for filename in request.form.getlist("files"):
        remove_file = Path(key).joinpath(filename)
        if project_path.joinpath(remove_file).is_file():
            manager.remove_file(source_path=remove_file.as_posix())
            opencontrol.remove(
                project_path=project_path.as_posix(),
                key=key,
                attribute=Path(remove_file).as_posix(),
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )
