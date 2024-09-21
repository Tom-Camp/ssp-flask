from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, request, url_for

from app.projects.helpers import get_project_data

opencontrol_bp = Blueprint("opencontrol", __name__, url_prefix="/project")


@opencontrol_bp.route("/<project_name>/opencontrol", methods=["GET"])
def show_opencontrol(project_name: str):
    """
    Returns a list of Components available to add to a Project.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)

    data: dict = {
        "project": project,
        "opencontrol": opencontrol.model_dump(),
    }

    return render_template("opencontrol/show_opencontrol.html", **data)


@opencontrol_bp.route("/<project_name>/templates/components", methods=["GET"])
def list_component_templates(project_name: str):
    """
    Returns a list of Components available to add to a Project.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)
    components = manager.get_directory_tree(
        project_path.joinpath("templates/components")
    )

    data: dict = {
        "project": project,
        "components": components,
    }

    return render_template("opencontrol/show_component_template.html", **data)


@opencontrol_bp.route("/<project_name>/files/add/<directory>", methods=["GET"])
def add_opencontrol_files(project_name: str, directory: str):
    """
    A page to add OpenControl certifications and standards.

    :param project_name: str - machine_name for the Project.
    :param directory: str - either standards or certifications
    :return: HTML template
    """
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)
    allowed_directories = ["appendices", "opencontrol", "frontmatter", "tailoring"]
    if not project_path.exists() or directory not in allowed_directories:
        abort(404)

    project_templates = manager.get_files_by_directory(f"templates/{directory}")
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

    return render_template("project/add_files.html", **data)


@opencontrol_bp.route("/<project_name>/<key>/add", methods=["GET"])
def add_opencontrol_values(project_name: str, key: str):
    """
    A view for list Components from the library.

    :param project_name: str - Project machine_name
    :param key: str - The OpenControl parameter
    :return: HTML template
    """
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)
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
    return render_template("opencontrol/edit_component_template.html", **data)


@opencontrol_bp.route("<project_name>/component/add", methods=["POST"])
def add_component_submit_handler(project_name: str):
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)

    for filename in request.form.getlist("files"):
        copy_path = Path("templates/components").joinpath(filename)
        destination = project_path.joinpath(copy_path)
        if project.library.library.joinpath(copy_path).is_dir():
            project.library.copy_directory(
                source_path=copy_path,
                destination_path=destination,
            )

            opencontrol.add(
                project_path=project_path,
                key="components",
                attribute=f"rendered_files/components/{filename}",
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/component/remove", methods=["POST"])
def remove_component_submit_handler(project_name: str):
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)

    for filename in request.form.getlist("files"):
        remove_path = Path("templates/components").joinpath(filename)
        if project_path.joinpath(remove_path).is_dir():
            manager.remove_directory(source=remove_path)

            opencontrol.remove(
                project_path=project_path,
                key="components",
                attribute=f"rendered_files/components/{filename}",
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/opencontrol/add", methods=["POST"])
def add_file_submit_handler(project_name: str):
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)

    key = request.form.get("key")
    if key not in ["certifications", "standards"]:
        abort(404)

    for filename in request.form.getlist("files"):
        copy_path = Path(key).joinpath(filename)
        destination = project_path.joinpath(copy_path)
        if project.library.library.joinpath(copy_path).is_file():
            project.library.copy_file(
                source_path=copy_path,
                destination_path=destination,
            )

            opencontrol.add(
                project_path=project_path,
                key=key,
                attribute=f"{key}/{filename}",
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/opencontrol/remove", methods=["POST"])
def remove_file_submit_handler(project_name: str):
    project_path, project, manager, opencontrol, _ = get_project_data(project_name)

    key = request.form.get("key")
    for filename in request.form.getlist("files"):
        remove_file = Path(key).joinpath(filename)
        if project_path.joinpath(remove_file).is_file():
            manager.remove_file(source_path=remove_file)
            opencontrol.remove(
                project_path=project_path,
                key=key,
                attribute=Path(remove_file).as_posix(),
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )
