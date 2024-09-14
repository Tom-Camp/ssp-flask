import shutil
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

    def get_files_by_directory(self, directory: str) -> list:
        return [file.name for file in self.project_path.joinpath(directory).glob("*")]

    def get_directory_tree(self, dir_path: Path) -> dict:
        if dir_path.is_dir():
            return {
                item.name: self.get_directory_tree(item) if item.is_dir() else None
                for item in dir_path.iterdir()
            }
        return {}

    def remove_file(self, source_path: Path):
        source = self.project_path.joinpath(source_path)
        destination = self.project_path.joinpath("trash").joinpath(source_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            _ = source.replace(destination)
            logger.info(f"Manager action: Resource {source.name} moved to trash")
            flash(message=f"{source_path} moved to Project trash", category="success")
        except FileExistsError:
            flash(message=f"Error writing file to {destination}", category="error")
        finally:
            pass

    def remove_directory(self, source: Path):
        file_source = self.project_path.joinpath(source)
        trash_path = self.project_path.joinpath("trash").joinpath(source)
        if trash_path.exists() and trash_path.is_dir():
            shutil.rmtree(trash_path)
        try:
            shutil.move(src=file_source, dst=trash_path)
            logger.info(f"Manager action: Resource {file_source.name} moved to trash")
            flash(
                message=f"{file_source.name} moved to Project trash", category="success"
            )
        except shutil.Error as e:
            logger.info(f"Manager action: {e}")
            flash(
                message=f"{file_source.name} failed to move to Project trash",
                category="success",
            )
        finally:
            pass

    def write_file(self, file_path: str | Path, file_body: str):
        file = Path(file_path)
        write_path = (
            file
            if file.is_relative_to(self.template_path)
            else self.template_path.joinpath(file)
        )
        try:
            with open(write_path, "w") as fp:
                fp.write(file_body)
            logger.info(f"Manager action: Template {write_path.name} updated")
            flash(message=f"{write_path.name} updated", category="success")
        except FileNotFoundError:
            logger.info(f"Manager action: Failed to update {write_path.name}")
            flash(message=f"{write_path.name} not found", category="error")
        except IOError:
            logger.info(f"Manager action: Error updating {write_path.name}")
            flash(message=f"Error updating {write_path.name}", category="error")
