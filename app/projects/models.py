from pathlib import Path
from typing import List, Optional

import rtyaml
from flask import flash
from pydantic import BaseModel, Field

from app.utils.library import Library
from config import ROOT_DIR


class Metadata(BaseModel):
    description: str
    maintainers: Optional[List[str]] = Field(default=[])


class OpenControl(BaseModel):
    schema_version: str = "1.0.0"
    name: str
    metadata: Optional[Metadata]
    components: List[str] = Field(default=[])
    certifications: List[str] = Field(default=[])
    standards: List[str] = Field(default=[])

    def __init__(self, name: str, description: str, maintainers: list):
        metadata = Metadata(
            description=description,
            maintainers=maintainers,
        )
        super().__init__(
            name=name,
            metadata=metadata,
        )

    def write(self, project_path: str):
        opencontrol_path = (
            ROOT_DIR.joinpath(project_path).joinpath("opencontrol").with_suffix(".yaml")
        )
        with opencontrol_path.open("w+") as oc:
            oc.write(rtyaml.dump(self.model_dump()))


class Project(BaseModel):
    name: str
    description: str
    machine_name: Optional[str]
    project_dir: Optional[str]
    project_path: Path = Field(Path())
    library: Optional[Library]

    def __init__(self, name: str, description: str, **kwargs):
        machine_name = self._get_machine_name(name=name)
        project_path = (
            ROOT_DIR.joinpath("project_data")
            .joinpath(machine_name)
            .relative_to(ROOT_DIR)
        )
        project_dir = project_path.as_posix()
        library = Library()
        super().__init__(
            name=name,
            description=description,
            machine_name=machine_name,
            project_dir=project_dir,
            project_path=project_path,
            library=library,
        )

    def create(self):
        try:
            self.project_path.mkdir(exist_ok=False)
            project_file = (
                self.project_path.joinpath("project").with_suffix(".yaml").open("w+")
            )
            project_file.write(
                rtyaml.dump(self.model_dump(exclude={"project_path", "library"}))
            )
            self.library.copy_file(
                source_path="configuration.yaml", destination=self.project_dir
            )
        except FileExistsError:
            flash(f"Project {self.name} already exists.", "is-danger")
        finally:
            flash(f"Project created at {self.project_dir}", "is-success")

    def get_project_files(self) -> list:
        return [file.as_posix() for file in self.project_path.rglob("*")]

    def get_project_files_by_directory(self, directory: str) -> list:
        return [file.name for file in self.project_path.joinpath(directory).glob("*")]

    def get_copy_destination(self, filepath: str) -> str:
        return self.project_path.joinpath(filepath).as_posix()

    @staticmethod
    def _get_machine_name(name: str) -> str:
        to_replace = "~`!@#$%^&*()+=[]{}|:;\"'?/>.<,"
        for x in to_replace:
            name = name.replace(x, "")
        return name.replace(" ", "_").lower()
