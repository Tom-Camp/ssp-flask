import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from flask import flash


@dataclass
class Library:
    project_base_path: str

    @staticmethod
    def list_files(directory: str) -> list:
        files: list = []
        try:
            files = [
                (file.name, "/".join(file.parts[1:]))
                for file in Path("library").joinpath(directory).iterdir()
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

    @staticmethod
    def list_directories(directory: str = ""):
        dirs: list = []
        try:
            dirs = [
                file.name
                for file in Path("library").joinpath(directory).iterdir()
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

    @staticmethod
    def get_directory_tree(directory: str = "") -> dict:
        directory_dict: dict = {}
        for root, dirs, files in os.walk(
            Path("library").joinpath(directory).as_posix()
        ):
            current_dict = directory_dict
            for part in os.path.relpath(root, directory).split(os.sep):
                if part != ".":
                    current_dict = current_dict.setdefault(part, {})
            for file in files:
                current_dict[file] = None
        return directory_dict

    def copy(self, filepath: str) -> str:
        source = Path("library").joinpath(filepath).as_posix()
        destination = self._get_destination(library_path=source)

        try:
            shutil.copytree(src=Path(source), dst=Path(destination), dirs_exist_ok=True)
            flash(message=f"{source} copied to {destination}", category="is-success")
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
            return destination

    def remove(self, filepath: str):
        destination = self._get_destination(library_path=filepath)
        try:
            Path(destination).unlink(missing_ok=False)
            flash(
                message=f"File {destination} removed from project.",
                category="is-success",
            )
        except FileNotFoundError:
            flash(
                message=f"The file {destination} was not found.", category="is-dander"
            )
        finally:
            pass

    def _get_destination(self, library_path: str) -> str:
        destination = "/".join(Path(library_path).parts[1:])
        return Path(self.project_base_path).joinpath(destination).as_posix()
