import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app')))
from app import app

client = TestClient(app)

test_restaurant = {
    "name": "Restaurante Teste",
    "cep": "01001-000",
    "cnpj": "12345678000199",
    "phone_number": "11999999999",
    "cuisine_type": "Italiana",
    "rating": 4.5,
    "is_open": True,
    "occupancy": 20,
    "max_occupancy": 50
}

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Criação inicial
    client.post("/restaurant/create", json=test_restaurant)
    yield
    # Cleanup
    client.delete(f"/restaurant/{test_restaurant['cnpj']}")

def test_create_duplicate_restaurant():
    response = client.post("/restaurant/create", json=test_restaurant)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_restaurant_success():
    response = client.get(f"/restaurant?name={test_restaurant['name']}")
    assert response.status_code == 200
    assert response.json()["cnpj"] == test_restaurant["cnpj"]

def test_update_restaurant_success():
    update_data = test_restaurant.copy()
    update_data["phone_number"] = "11888888888"
    response = client.put(f"/restaurant/{test_restaurant['cnpj']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["phone_number"] == "11888888888"

def test_update_occupancy_success():
    response = client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 30}
    )
    assert response.status_code == 200
    assert response.json()["occupancy"] == 30

def test_update_occupancy_above_max():
    response = client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 100}
    )
    assert response.status_code == 400
    assert "maximum limit" in response.json()["detail"]

def test_update_occupancy_when_closed():
    client.post(f"/restaurant/{test_restaurant['cnpj']}", json={**test_restaurant, "is_open": False})
    response = client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 10}
    )
    assert response.status_code == 400
    assert "closed" in response.json()["detail"]

    # Reabrir restaurante
    client.post(f"/restaurant/{test_restaurant['cnpj']}", json={**test_restaurant, "is_open": True})

def test_delete_restaurant_success():
    response = client.delete(f"/restaurant/{test_restaurant['cnpj']}")
    assert response.status_code == 204

def test_get_deleted_restaurant():
    response = client.get(f"/restaurant?name={test_restaurant['name']}")
    assert response.status_code == 404
