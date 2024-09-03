from pathlib import Path

from app.utils.library import Library


def test_project_create(project):
    assert project.name == "Testing Project!"


def test_project_machine_name(project):
    assert project.machine_name == "testing_project"


def test_project_path(project):
    assert isinstance(project.project_path, Path)


def test_project_directory(project):
    assert project.project_path.as_posix() == "project_data/testing_project"


def test_project_project_file(project):
    assert project.project_path.joinpath("project").with_suffix(".yaml").is_file


def test_project_configuration_file(project):
    assert project.project_path.joinpath("configuration").with_suffix(".yaml").is_file


def test_project_opencontrol_file(project):
    assert project.project_path.joinpath("opencontrol").with_suffix(".yaml").is_file


def test_project_library(project):
    assert isinstance(project.library, Library)
