import shutil
from dataclasses import dataclass
from pathlib import Path

from flask import flash

from app.logging_config import loguru_logger as logger
from config import config

ROOT_DIR = config.get("ROOT_DIR", Path())


@dataclass
class Library:
    library: Path = ROOT_DIR.joinpath("app").joinpath("library").relative_to(ROOT_DIR)  # type: ignore

    def list_files(self, directory: str) -> list:
        files: list = []
        try:
            files = [
                file.name
                for file in self.library.joinpath(directory).iterdir()
                if file.is_file()
            ]
        except FileNotFoundError:
            flash(message=f"{directory} was not found.", category="is-danger")
        except PermissionError:
            flash(
                message=f"Permission denied. Cannot read {directory}.",
                category="is-danger",
            )
        except Exception as e:
            flash(message=f"An error occurred: {e}", category="is-danger")
        finally:
            pass
        return files

    def list_directories(self, directory: str):
        dirs: list = []
        try:
            dirs = [
                file.name
                for file in self.library.joinpath(directory).iterdir()
                if file.is_dir()
            ]
        except FileNotFoundError:
            flash(message=f"{directory} was not found.", category="is-danger")
        except PermissionError:
            flash(
                message=f"Permission denied. Cannot read {directory}.",
                category="is-danger",
            )
        except Exception as e:
            flash(message=f"An error occurred: {e}", category="is-danger")
        finally:
            return dirs

    def copy_file(self, source_path: str, destination_path: str) -> str:
        source = self.library.joinpath(source_path)
        destination = Path(destination_path)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src=source, dst=destination)
            flash(
                message=f"{source.name} copied to {'/'.join(destination.parts[-3:-1])}",
                category="is-success",
            )
            logger.info(f"{source.name} copied to {'/'.join(destination.parts[-3:-1])}")
        except FileNotFoundError:
            flash(message=f"{source} was not found.", category="is-danger")
        except PermissionError:
            flash(
                message=f"Permission denied. Cannot copy {source} to {destination}.",
                category="is-danger",
            )
        except Exception as e:
            flash(message=f"An error occurred: {e}", category="is-danger")
        finally:
            return destination.as_posix()

    def copy_directory(self, source_path: str, destination_path: str) -> str:
        source = self.library.joinpath(source_path)
        destination = Path(destination_path)

        try:
            shutil.copytree(src=source, dst=destination, dirs_exist_ok=True)
            flash(message=f"{source} copied to {destination}", category="is-success")
            logger.info(f"Library: {source.name} copied to {destination.as_posix()}.")
        except FileNotFoundError:
            flash(message=f"{source} was not found.", category="is-danger")
        except PermissionError:
            flash(
                message=f"Permission denied. Cannot copy {source} to {destination}.",
                category="is-danger",
            )
        except Exception as e:
            flash(message=f"An error occurred: {e}", category="is-danger")
        finally:
            return destination.as_posix()
