from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI + Pydantic"}


def test_create_and_get_item():
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    item_id = response.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_create_item_validation_error():
    response = client.post("/items", json={"name": "Bad", "price": -1})
    assert response.status_code == 422


def test_get_missing_item():
    response = client.get("/items/999")
    assert response.status_code == 404
