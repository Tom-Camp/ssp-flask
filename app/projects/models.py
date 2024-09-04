from pathlib import Path

import rtyaml
from flask import flash
from pydantic import BaseModel, Field, model_validator

from app.logging_config import loguru_logger as logger
from app.toolkit.opencontrol import Metadata, OpenControl
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
            self.add_base()
            logger.info(f"Project: Project {self.name} created.")
        except FileExistsError:
            flash(message=f"Project {self.name} already exists.", category="error")
        finally:
            flash(
                message=f"Project created at {self.project_path.as_posix()}",
                category="success",
            )

    def add_base(self):
        self.library.copy_file(
            source_path="configuration.yaml",
            destination_path=self.project_path.joinpath(
                "configuration.yaml"
            ).as_posix(),
        )
        self.library.copy_directory(
            source_path="keys",
            destination_path=self.project_path.joinpath("keys").as_posix(),
        )
        metadata = Metadata(
            description=self.description,
            maintainers=[],
        )
        OpenControl(
            name=self.name,
            metadata=metadata,
        ).write(self.project_path.as_posix())

    @staticmethod
    def _get_machine_name(name: str) -> str:
        to_replace = "~`!@#$%^&*()+=[]{}|:;\"'?/>.<,"
        for x in to_replace:
            name = name.replace(x, "")
        return name.replace(" ", "_").lower()
