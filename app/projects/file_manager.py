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
            return dict(
                sorted(
                    {
                        item.name: (
                            self.get_directory_tree(item) if item.is_dir() else None
                        )
                        for item in dir_path.iterdir()
                    }.items()
                )
            )
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

    def write_file(self, file_path: Path, file_body: str):
        output = self.project_path.joinpath(file_path)
        if not output.parent.is_dir():
            output.parent.mkdir(parents=True)

        try:
            with open(output, "w+") as fp:
                fp.write(file_body)
            logger.info(f"Manager action: Template {output.name} updated")
            flash(message=f"{output.name} updated", category="success")
        except IOError:
            logger.error(f"Manager action: Error updating {output.name}")
            flash(message=f"Error updating {output.name}", category="error")

    def read_file(self, file_path: Path) -> str:
        rendered = self.project_path.joinpath(file_path)
        if rendered.exists():
            return rendered.read_text(encoding="utf-8")
        else:
            flash(f"File {file_path} does not exist.", category="error")
            return ""
