import shutil
from dataclasses import dataclass
from pathlib import Path

from flask import flash


@dataclass
class Library:
    project_path: str

    def copy(self, filename: str, dest: str | None):
        source = Path("library").joinpath(filename)
        destination = (
            Path(self.project_path).joinpath(dest) if dest else Path(self.project_path)
        )

        try:
            shutil.copy(source, destination)
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
