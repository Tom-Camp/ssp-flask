import pytest

from app import create_app
from app.projects.models import Project


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
    project_instance = Project(
        name="Testing Project!",
        description="This is a test project",
    )
    yield project_instance
