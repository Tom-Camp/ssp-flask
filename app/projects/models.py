from pathlib import Path

import rtyaml
from flask import flash
from pydantic import BaseModel, Field, model_validator

from app.utils.library import Library
from config import Config

ROOT_DIR = Config.ROOT_DIR


class Project(BaseModel):
    name: str
    description: str
    machine_name: str | None = None
    project_path: Path = None  # type: ignore
    library: Library = Field(Library())

    @model_validator(mode="after")
    def set_project_path(cls, model):
        if not model.machine_name:
            model.machine_name = cls._get_machine_name(name=model.name)
        model.project_path = (
            ROOT_DIR.joinpath("project_data")
            .joinpath(model.machine_name)
            .relative_to(ROOT_DIR)
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
                source_path="configuration.yaml",
                destination_path=self.project_path.joinpath(
                    "configuration.yaml"
                ).as_posix(),
            )
        except FileExistsError:
            flash(f"Project {self.name} already exists.", "is-danger")
        finally:
            flash(f"Project created at {self.project_path.as_posix()}", "is-success")

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
