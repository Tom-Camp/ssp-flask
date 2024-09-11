from dataclasses import dataclass
from pathlib import Path

from app.projects.file_manager import FileManager
from app.utils.helpers import load_yaml

default_keys: dict = {
    "artifacts.yaml": "artifact",
    "config-management.yaml": "cm",
    "info_system.yaml": "information_system",
    "justifications.yaml": "justify",
}


@dataclass
class Config:
    project_name = str
    project_path = Path
    config: dict
    config_path: Path
    keys: str
    config_files: list

    def __init__(self, machine_name: str):
        manager = FileManager(project_machine_name=machine_name)
        self.project_path = manager.project_path  # type: ignore
        self.config_path = self.project_path.joinpath("configuration").with_suffix(  # type: ignore
            ".yaml"
        )
        self.keys = self.project_path.joinpath("keys").as_posix()  # type: ignore
        self.config = load_yaml(filename=self.config_path.as_posix())
        self.load_keys()

    def load_keys(self):
        self.config_files = []
        for filename in Path(self.keys).glob("*.yaml"):
            key = default_keys.get(filename.name, filename.stem)
            data = load_yaml(filename=filename.as_posix())
            if data:
                self.config_files.append((filename.name, key))
                self.config[key] = data
