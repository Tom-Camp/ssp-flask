from pathlib import Path

from app.toolkit.opencontrol import Component
from app.utils.helpers import load_yaml, write_yaml


def get_components_directories(project_path: Path) -> list:
    dir_path = project_path.joinpath("templates").joinpath("components")
    if not dir_path.is_dir():
        dir_path.mkdir(parents=True)
        return []
    return [directories.name for directories in dir_path.glob("*")]


def get_component_files(project_path: Path, component: str) -> list:
    templates: list = []
    component_path = (
        project_path.joinpath("templates").joinpath("components").joinpath(component)
    )
    if component_path.is_dir():
        templates = [
            file.name
            for file in component_path.glob("*.yaml")
            if file.name != "component.yaml"
        ]
    return templates


def update_opencontrol_component(added_file: str):
    file = Path(added_file)
    component = Path(file).parent
    component_file_path = component.joinpath("component").with_suffix(".yaml")
    if component_file_path.is_file():
        component_file = load_yaml(component_file_path.as_posix())
        component_file["satisfies"].append(file.name)
        write_yaml(filename=component_file_path.as_posix(), data=component_file)
    else:
        component_file_path.touch()
        create_opencontrol_component(
            name=component.name,
            file=file.name,
            component_file=component_file_path.as_posix(),
        )


def create_opencontrol_component(name: str, file: str, component_file: str):
    component = Component(
        name=name,
        satisfies=[file],
    )
    write_yaml(
        filename=component_file,
        data=component.model_dump(),
    )
