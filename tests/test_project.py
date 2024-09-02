from app.utils.library import Library


def test_project_create(project):
    assert project.name == "Test Project!"


def test_project_machine_name(project):
    assert project.machine_name == "test_project"


def test_project_directory(project):
    assert project.project_path.is_dir()


def test_project_library(project):
    assert isinstance(project.library, Library)


def test_project_page(client, project):
    response = client.get(f"project/{project.machine_name}")
    assert response.status_code == 200


def test_project_template_appendices_pages(client, project):
    response = client.get(f"project/{project.machine_name}/templates/appendices")
    assert response.status_code == 200


def test_project_template_frontmatter_pages(client, project):
    response = client.get(f"project/{project.machine_name}/templates/frontmatter")
    assert response.status_code == 200


def test_project_template_tailoring_pages(client, project):
    response = client.get(f"project/{project.machine_name}/templates/tailoring")
    assert response.status_code == 200


def test_project_template_components_pages(client, project):
    response = client.get(f"project/{project.machine_name}/templates/tailoring")
    assert response.status_code == 200
