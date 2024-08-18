import shutil
from dataclasses import dataclass
from pathlib import Path

from flask import flash


@dataclass
class Library:
    project_path: str

    @staticmethod
    def list_files(dirname: str) -> list:
        files: list = []
        try:
            files = [
                (file.name, file.as_posix().replace("libary/", ""))
                for file in Path("library").joinpath(dirname).glob("*")
            ]
        except FileNotFoundError:
            flash(f"{dirname} was not found.")
        except PermissionError:
            print(f"Permission denied. Cannot read {dirname}.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            pass
        return files

    def copy(self, filename: str, dest: str | None):
        source = Path("library").joinpath(filename)
        destination = (
            Path(self.project_path).joinpath(dest) if dest else Path(self.project_path)
        )

        try:
            shutil.copy(src=source, dst=destination)
        except FileNotFoundError:
            flash(f"{source.as_posix()} was not found.")
        except PermissionError:
            print(
                f"Permission denied. Cannot copy {source.as_posix()} to {destination.as_posix()}."
            )
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            pass

    def remove(self, filename: str):
        try:
            Path(self.project_path).joinpath(filename).unlink(missing_ok=False)
            flash(f"File {filename} removed from project.", "success")
        except FileNotFoundError:
            flash(f"The file {filename} was not found.", "error")
        finally:
            pass
