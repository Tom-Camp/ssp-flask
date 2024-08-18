from pathlib import Path

from app.utils.helpers import load_yaml, scan_dir


def get_projects() -> list:
    """
    Creates a list of projects in the project_data directory.

    :return: list
    """
    projects: list = []
    project_list = scan_dir(Path("project_data").as_posix())
    for project in project_list:
        project_file = Path(project).joinpath("project").with_suffix(".yaml")
        if project_file.exists():
            project_data = load_yaml(project_file.as_posix())
            projects.append(project_data)
    return projects
