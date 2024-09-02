from pathlib import Path

from flask import flash
from pydantic import BaseModel, model_validator

from app.logging_config import loguru_logger as logger
from config import config

ROOT_DIR = config.get("ROOT_DIR", Path())


class FileManager(BaseModel):
    project_machine_name: str
    template_path: Path = None  # type: ignore
    project_path: Path = None  # type: ignore

    @model_validator(mode="after")
    def set_template_path(cls, model):
        model.project_path = ROOT_DIR.joinpath("project_data").joinpath(
            model.project_machine_name
        )
        if model.project_path.is_dir():
            model.template_path = model.project_path.joinpath("templates")

    def get_files(self) -> list:
        return [file.as_posix() for file in self.template_path.rglob("*")]

    def get_files_by_directory(self, directory: str) -> list:
        return [file.name for file in self.template_path.joinpath(directory).glob("*")]

    def get_copy_destination(self, filepath: str) -> str:
        return self.template_path.joinpath(filepath).as_posix()

    def remove_file(self, source_path: str):
        source = self.project_path.joinpath(source_path)
        destination = self.project_path.joinpath("trash").joinpath(source_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            _ = source.replace(destination)
            logger.info(f"Manager action: Resource {source.name} moved to trash")
            flash(
                message=f"{source_path} moved to Project trash", category="is-success"
            )
        except FileExistsError as e:
            logger.exception(f"Manager error: {e}")
            flash(message=f"Error writing file to {destination}", category="is-danger")
        finally:
            pass
