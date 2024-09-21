from pathlib import Path

import markdown
from flask import Blueprint, abort, render_template, request

from app.projects.helpers import get_project_data

rendered_bp = Blueprint("rendered", __name__, url_prefix="/project")


@rendered_bp.route("<project_name>/rendered", methods=["GET"])
def rendered_files(project_name: str):
    """
    Returns a form for editing a template.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, manager, _, _ = get_project_data(project_name)
    rendered: dict = manager.get_directory_tree(
        dir_path=project_path.joinpath("rendered")
    )
    data: dict = {
        "project": project,
        "rendered": dict(sorted(rendered.items())),
    }

    return render_template("rendered/list_rendered_files.html", **data)


@rendered_bp.route("<project_name>/rendered/view", methods=["GET"])
def rendered_file_view(project_name: str):
    """
    Returns a form for editing a template.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, manager, _, _ = get_project_data(project_name)
    file_path = request.args.get("filepath")
    if not file_path:
        abort(404)

    file = Path("rendered").joinpath(file_path)
    file_body = manager.read_file(file_path=file)

    if not file_body:
        abort(404)

    data: dict = {
        "project": project,
        "filename": file.name,
        "filepath": "/".join(file.parts[-2:]),
        "body": file_body if file.suffix == ".yaml" else markdown.markdown(file_body),
        "yaml": True if file.suffix == ".yaml" else False,
    }

    return render_template("rendered/show_rendered_file.html", **data)
