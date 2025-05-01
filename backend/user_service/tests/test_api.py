import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from fastapi.testclient import TestClient
from app import app  

client = TestClient(app)
def test_create_user():
    response = client.post(
        "/user/create", json={"email": "user@example.com", "name": "User Example", "password": "12345"}
    )
    assert response.status_code == 201 or response.status_code == 200
    assert response.json()["email"] == "user@example.com"

def test_get_user():
    response = client.get("/user?email=user@example.com")
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"

def test_get_user_not_found():
    response = client.get("/user?email=nonexistent@example.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
