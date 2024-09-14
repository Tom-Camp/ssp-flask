from pathlib import Path

from app.projects.file_manager import FileManager
from app.projects.models import Project
from app.toolkit.base.config import Config
from app.toolkit.opencontrol import OpenControl
from app.utils.helpers import load_yaml, scan_dir
from config import config

ROOT_DIR = config.get("ROOT_DIR", Path())


def get_destination_path(file: str) -> str:
    """
    Given a library path and a Project machine_name, return a file path to use
    to copy the library file into the Project.

    :param file: str - the library file path
    :return: str - the file path in the Project directory
    """
    return "/".join(Path(file).parts[1:])


def get_project_data(
    project_name: str,
) -> tuple[Path, Project, FileManager, OpenControl, Config]:
    """
    Return a loaded Project, a pathlib Path representation of Project path, and an
    instance of a Library.

    :param project_name: str - the Project machine_name.
    :return: tuple (Path, Project, Library)
    """
    project_machine_name = project_name.lower()
    project_path = (
        ROOT_DIR.joinpath("project_data")  # type: ignore
        .joinpath(project_machine_name.lower())  # type: ignore
        .relative_to(ROOT_DIR)  # type: ignore
    )
    project = load_project(project_name=project_machine_name)
    manager = FileManager(project_machine_name=project_machine_name)
    oc_path = project_path.joinpath("opencontrol").with_suffix(".yaml")
    oc_data = load_yaml(oc_path.as_posix())
    opencontrol = OpenControl(**oc_data)
    config = Config(machine_name=project_machine_name)
    return project_path, project, manager, opencontrol, config


def load_project(project_name: str) -> Project:
    """
    Return a Project object.

    :param project_name: str the Project machine_name
    :return: Project
    """
    project_file = load_yaml(
        Path("project_data")
        .joinpath(project_name)
        .joinpath("project")
        .with_suffix(".yaml")
        .as_posix()
    )
    return Project(**project_file)


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


def get_machine_name(name: str) -> str:
    to_replace = "~`!@#$%^&*()+=[]{}|:;\"'?/>.<,"
    for x in to_replace:
        name = name.replace(x, "")
    return name.replace(" ", "_").lower()


def load_template_file(template_path: str) -> str:
    template_file = Path(template_path)
    text: str = ""
    if template_file.is_file():
        text = template_file.read_text(encoding="utf-8")
    return text
