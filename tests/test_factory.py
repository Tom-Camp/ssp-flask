from app import create_app


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_index(client):
    response = client.get("/")
    assert b"The SSP Toolkit is used" in response.data


def test_not_found(client):
    response = client.get("/notfound")
    assert response.status_code == 404
