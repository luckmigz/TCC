import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ajuste dos caminhos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app import app

client = TestClient(app)

# Dados de restaurante para testes
test_restaurant = {
    "name": "Restaurante Teste",
    "cep": "01001-000",
    "cnpj": "12345678000100",
    "phone_number": "11999999999",
    "cuisine_type": "Italiana",
    "rating": 4.5,
    "is_open": True,
    "occupancy": 20,
    "max_occupancy": 50
}

def test_create_restaurant():
    response = client.post("/restaurant/create", json=test_restaurant)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["cnpj"] == test_restaurant["cnpj"]

@pytest.fixture(scope="module", autouse=True)
def setup_restaurant():
    response = client.post("/restaurant/create", json=test_restaurant)
    assert response.status_code in (200, 201)

def test_update_occupancy_success():
    response = client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 30}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["occupancy"] == 30

def test_update_occupancy_above_max():
    response = client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 100}
    )
    assert response.status_code == 400
    assert "Occupancy cannot exceed" in response.json()["detail"]

def test_update_occupancy_closed_restaurant():
    # Fecha o restaurante
    client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/update",
        json={"is_open": False}
    )

    response = client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 10}
    )
    assert response.status_code == 400
    assert "must be open" in response.json()["detail"]

    # Reabre para evitar efeito colateral em outros testes
    client.patch(
        f"/restaurant/{test_restaurant['cnpj']}/update",
        json={"is_open": True}
    )
