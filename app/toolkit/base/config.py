from pathlib import Path

import yaml


class Config:
    config: dict
    configuration: Path = Path("configuration.yaml")
    keys: Path = Path("keys")
    config_files: list[()] = []
    default_keys: dict = {
        "artifacts.yaml": "artifact",
        "config-management.yaml": "cm",
        "info_system.yaml": "information_system",
        "justifications.yaml": "justify",
    }

    def __init__(self):
        if self.configuration.exists():
            try:
                with open(self.configuration, "r") as fp:
                    self.config = yaml.load(fp, Loader=yaml.FullLoader)
            except IOError:
                print(f"Error loading {self.configuration.as_posix}.")
        else:
            raise FileNotFoundError("configuration.yaml not found in project root.")
        self.load_keys()

    def load_keys(self):
        for filename in self.keys.glob("*.yaml"):
            key = self.default_keys.get(filename.name, filename.stem)
            self.config_files.append((filename.name, key))
            with open(filename, "r") as fp:
                self.config[key] = yaml.load(fp, Loader=yaml.FullLoader)

    def check_config_values(self, file: str, key: str = "") -> str | dict:
        if key:
            values = self.config.get(file, {}).get(key, "")
        else:
            values = self.config.get(file, {})
        return values
