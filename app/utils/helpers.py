from pathlib import Path

import rtyaml
from flask import flash


def load_yaml(filename: str) -> dict:
    file: dict = {}
    try:
        with Path(filename).open("r") as fp:
            file = rtyaml.load(fp)
    except FileNotFoundError:
        flash(message=f"File {filename} does not exist", category="is-danger")
    except IOError:
        flash(message=f"Error loading {filename}", category="is-danger")
    finally:
        pass
    return file


def write_yaml(filename: str, data: dict):
    try:
        with Path(filename).open("w+") as fp:
            rtyaml.dump(data, fp)
        flash(message=f"Updating file {filename}.", category="is-success")
    except FileNotFoundError:
        flash(message=f"File {filename} does not exist", category="is-dander")
    except IOError:
        flash(message=f"Error loading {filename}", category="is-dander")
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
