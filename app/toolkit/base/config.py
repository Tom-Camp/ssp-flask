from dataclasses import dataclass
from pathlib import Path

from app.utils.helpers import load_yaml

default_keys: dict = {
    "artifacts.yaml": "artifact",
    "config-management.yaml": "cm",
    "info_system.yaml": "information_system",
    "justifications.yaml": "justify",
}


@dataclass
class Config:
    config: dict
    configuration: str
    keys: str
    config_files: list

    def __init__(self, config: str, keys: str):
        self.configuration = config
        self.keys = keys
        self.config = load_yaml(filename=self.configuration)
        self.load_keys()

    def load_keys(self):
        self.config_files = []
        for filename in Path(self.keys).glob("*.yaml"):
            key = default_keys.get(filename.name, filename.stem)
            data = load_yaml(filename=filename.as_posix())
            if data:
                self.config_files.append((filename.name, key))
                self.config[key] = data
