import sys
import os
import pytest
from fastapi.testclient import TestClient


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))  # Adiciona a raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))  # Adiciona o diretório app

from app import app  

client = TestClient(app)


test_restaurant = {
    "name": "Restaurante Teste",
    "cep": "01001-000",
    "cnpj": "12.345.678/0001-90",
    "phone_number": "11999999999",
    "cuisine_type": "Italiana",
    "rating": 4.5,
    "is_open": True,
    "occupancy": 20,
    "max_occupancy": 50
}

@pytest.fixture(scope="module", autouse=True)
def setup_restaurant():
    # Cria o restaurante antes dos testes
    client.post("/restaurants/create", json=test_restaurant)

def test_update_occupancy_success():
    response = client.patch(
        f"/restaurants/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 30}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["occupancy"] == 30

def test_update_occupancy_above_max():
    response = client.patch(
        f"/restaurants/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 100}
    )
    assert response.status_code == 400
    assert "Occupancy cannot exceed" in response.json()["detail"]

def test_update_occupancy_closed_restaurant():
    # Fecha o restaurante primeiro
    client.patch(f"/restaurants/{test_restaurant['cnpj']}", json={"is_open": False})

    response = client.patch(
        f"/restaurants/{test_restaurant['cnpj']}/occupancy",
        json={"occupancy": 10}
    )
    assert response.status_code == 400
    assert "must be open" in response.json()["detail"]
