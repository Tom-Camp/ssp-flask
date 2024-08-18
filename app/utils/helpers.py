from pathlib import Path

import rtyaml
from flask import flash


def get_machine_name(name: str) -> str:
    """
    Create a name to be used for a Project's directory within the project_data directory
    :param name: string The project name
    :return: string The project name only containing alphanumerics, dashes and underscores.
    """
    to_replace = "~`!@#$%^&*()+=[]{}|:;\"'?/>.<,"
    for x in to_replace:
        name = name.replace(x, "")
    return name.replace(" ", "_").lower()


def load_yaml(filename: str) -> dict:
    file: dict = {}
    try:
        with Path(filename).open("r") as fp:
            file = rtyaml.load(fp)
    except FileNotFoundError:
        flash(f"File {filename} does not exist", "error")
    except IOError:
        flash(f"Error loading {filename}", "error")
    finally:
        pass
    return file


def write_yaml(filename: str, data: dict):
    try:
        with Path(filename).open("w+") as fp:
            rtyaml.dump(data, fp)
        flash(f"Updating file {filename}.", "success")
    except FileNotFoundError:
        flash(f"File {filename} does not exist", "error")
    except IOError:
        flash(f"Error loading {filename}", "error")
    finally:
        pass


def scan_dir(dirname: str) -> list:
    """
    Scan a directory and return a list of files within it.

    :param dirname: a string representing the directory name.
    :return: list of filenames
    """
    files: list = [filename for filename in Path(dirname).glob("*")]
    return files
