from flask import Blueprint, redirect, render_template, request, url_for

from app.projects.views import get_project_data

opencontrol_bp = Blueprint("component", __name__, url_prefix="/project")


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

    return render_template("components/component_templates.html", **data)


@opencontrol_bp.route("/<project_name>/components/add", methods=["GET"])
def components_add_list_view(project_name: str):
    """
    A view for list Components from the library.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, manager, opencontrol = get_project_data(project_name)
    components = project.library.list_directories(directory="templates/components")
    new_components: list = [
        comp for comp in components if comp not in opencontrol.components
    ]
    data: dict = {
        "project": project,
        "components": new_components,
        "project_components": opencontrol.components,
    }
    return render_template("components/components_add_list_view.html", **data)


@opencontrol_bp.route("<project_name>/component/add", methods=["POST"])
def component_add_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    for component in request.form.getlist("files"):
        copy_path = f"templates/components/{component}"
        destination = project_path.joinpath(copy_path)
        if project.library.library.joinpath(copy_path).is_dir():
            project.library.copy_directory(
                source_path=copy_path, destination_path=destination.as_posix()
            )
        if component not in opencontrol.components:
            opencontrol.update(
                project_path=project_path.as_posix(),
                key="components",
                action="add",
                attribute=component,
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )


@opencontrol_bp.route("<project_name>/component/remove", methods=["POST"])
def component_remove_submit(project_name: str):
    project_path, project, manager, opencontrol = get_project_data(project_name)

    for component in request.form.getlist("files"):
        copy_path = f"templates/components/{component}"
        manager.remove_file(source_path=copy_path)
        if component in opencontrol.components:
            opencontrol.update(
                project_path=project_path.as_posix(),
                key="components",
                action="remove",
                attribute=component,
            )

    return redirect(
        request.referrer or url_for("project.project_view", project_name=project_name)
    )
