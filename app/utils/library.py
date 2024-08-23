import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from flask import flash


@dataclass
class Library:
    project_machine_name: str

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
            flash(f"{directory} was not found.")
        except PermissionError:
            print(f"Permission denied. Cannot read {directory}.")
        except Exception as e:
            print(f"An error occurred: {e}")
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
            flash(f"{directory} was not found.")
        except PermissionError:
            print(f"Permission denied. Cannot read {directory}.")
        except Exception as e:
            print(f"An error occurred: {e}")
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
        destination = self._get_destination(filepath=filepath)

        try:
            shutil.copytree(src=source, dst=destination, dirs_exist_ok=True)
            flash(f"{source} copied to {destination}", "success")
        except FileNotFoundError:
            flash(f"{source} was not found.")
        except PermissionError:
            print(f"Permission denied. Cannot copy {source} to {destination}.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            return destination

    def remove(self, filepath: str):
        destination = self._get_destination(filepath=filepath)
        try:
            Path(destination).unlink(missing_ok=False)
            flash(f"File {destination} removed from project.", "success")
        except FileNotFoundError:
            flash(f"The file {destination} was not found.", "error")
        finally:
            pass

    def _get_destination(self, filepath: str) -> str:
        return (
            Path("project_data")
            .joinpath(self.project_machine_name)
            .joinpath(filepath)
            .as_posix()
        )
