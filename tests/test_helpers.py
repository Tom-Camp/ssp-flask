from pathlib import Path, PosixPath

from app.utils import helpers


def test_load_yaml():
    filepath = "tests/assets/test.yaml"
    load_yaml = helpers.load_yaml(filepath)
    assert type(load_yaml) is dict
    assert load_yaml.get("name").get("title") == "Test YAMl"


def test_write_yaml(client):
    _ = client.get("/")
    write_path = Path("tests/assets/write_test.yaml")
    filepath = "tests/assets/test.yaml"
    load_yaml = helpers.load_yaml(filepath)

    helpers.write_yaml(write_path.as_posix(), load_yaml)

    assert write_path.exists() is True
    write_path.unlink()


def test_scan_dir():
    files = helpers.scan_dir("tests/assets/scanme")
    assert len(files) == 4
    assert isinstance(files[0], PosixPath)
