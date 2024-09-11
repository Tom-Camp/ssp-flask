import pytest

from app import create_app
from app.projects.models import Project
from app.projects.views import get_machine_name


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "testing_secret_key",
        }
    )
    yield app


@pytest.fixture
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="module")
def project():
    name = "Testing Project!"
    machine_name = get_machine_name(name=name)
    project_instance = Project(
        name=name,
        machine_name=machine_name,
        description="This is a test project",
    )
    yield project_instance
