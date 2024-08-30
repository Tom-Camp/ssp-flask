from flask import Blueprint, render_template, request

from app.components.views import (
    get_component_files,
    get_components_directories,
    update_opencontrol_component,
)
from app.projects.views import get_project_request_defaults

component_bp = Blueprint("component", __name__, url_prefix="/project")


@component_bp.route("/<project_name>/components", methods=["GET"])
def components_list_view(project_name: str):
    """
    Returns a list of Components available to add to a Project.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project = get_project_request_defaults(project_name)
    component_directories = get_components_directories(project_path)

    data: dict = {
        "directory": "components",
        "project": project,
        "components": component_directories,
    }

    return render_template("components/component_list.html", **data)


@component_bp.route("/<project_name>/components/add", methods=["GET"])
def components_add_list_view(project_name: str):
    """
    A view for list Components from the library.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project = get_project_request_defaults(project_name)
    components = project.library.list_directories(directory="templates/components")
    data: dict = {"project": project, "components": components}
    return render_template("components/component_add.html", **data)


@component_bp.route(
    "/<project_name>/components/add/<component>", methods=["GET", "POST"]
)
def components_add_component_view(project_name: str, component: str):
    """
    A view for adding Components or individual component files.

    :param project_name: str - Project machine_name
    :param component: str - Component name
    :return: HTML template
    """
    project_path, project = get_project_request_defaults(project_name)

    if request.method == "POST":
        for file in request.form.getlist("files[]"):
            copy_path = f"templates/{file}"
            destination = project_path.joinpath(copy_path)
            if project.library.library.joinpath(copy_path).is_dir():
                project.library.copy_directory(
                    copy_path, destination_path=destination.as_posix()
                )
            else:
                added_file = project.library.copy_file(
                    source_path=copy_path, destination_path=destination.as_posix()
                )
                update_opencontrol_component(added_file)
    project_templates = get_component_files(
        project_path=project_path, component=component
    )
    templates = project.library.list_files(
        directory=f"templates/components/{component}"
    )
    data: dict = {
        "component": component,
        "project": project,
        "project_templates": project_templates,
        "library_templates": templates,
    }
    return render_template("components/component_add_component.html", **data)
