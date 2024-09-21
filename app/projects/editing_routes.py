from pathlib import Path

from flask import Blueprint, redirect, render_template, request, url_for

from app.projects.helpers import get_project_data, load_template_file
from app.toolkit.createfiles import render

editing_bp = Blueprint("editing", __name__, url_prefix="/project")


@editing_bp.route("<project_name>/template/edit", methods=["POST"])
def edit_template(project_name: str):
    """
    Returns a form for editing a template.

    :param project_name: str - Project machine_name
    :return: HTML template
    """
    project_path, project, _, _, _ = get_project_data(project_name)

    template_path = Path(request.form.get("template"))
    file_value = load_template_file(template_path=template_path)
    relative_path = template_path.relative_to(project_path.joinpath("templates"))

    data: dict = {
        "project": project,
        "file_path": relative_path,
        "file_name": template_path.name,
        "directory": relative_path.parts[0],
        "file_value": file_value,
    }

    return render_template("editing/file_editing.html", **data)


@editing_bp.route("<project_name>/template/submit", methods=["POST"])
def edit_template_submit_handler(project_name: str):
    project_path, project, manager, _, config = get_project_data(project_name)
    file_text = request.form.get("file_body")
    file_path = request.form.get("file_path")
    directory = request.form.get("directory")
    update_path = Path("templates").joinpath(file_path)
    manager.write_file(
        file_path=update_path,
        file_body=file_text,
    )
    render(
        templates=[file_path],
        project_path=project_path,
        config=config,
        manager=manager,
    )

    return redirect(
        url_for(
            "project.project_templates_view",
            project_name=project_name,
            directory=directory,
        )
    )
