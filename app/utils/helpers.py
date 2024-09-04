from pathlib import Path

import rtyaml
from flask import flash


def load_yaml(filename: str) -> dict:
    file: dict = {}
    try:
        with Path(filename).open("r") as fp:
            file = rtyaml.load(fp)
    except FileNotFoundError:
        flash(message=f"File {filename} does not exist", category="error")
    except IOError:
        flash(message=f"Error loading {filename}", category="error")
    finally:
        pass
    return file


def write_yaml(filename: str, data: dict):
    try:
        with Path(filename).open("w+") as fp:
            rtyaml.dump(data, fp)
        flash(message=f"Updating file {filename}.", category="success")
    except FileNotFoundError:
        flash(message=f"File {filename} does not exist", category="error")
    except IOError:
        flash(message=f"Error loading {filename}", category="error")
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
