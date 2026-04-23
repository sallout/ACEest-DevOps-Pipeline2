import pytest
from app import app, clients

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Reset state before each test
        clients.clear()
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"ACEest Fitness API" in response.data

def test_get_programs(client):
    response = client.get('/programs')
    assert response.status_code == 200
    data = response.get_json()
    assert "Fat Loss (FL)" in data['data']

def test_register_client_success(client):
    payload = {
        "name": "Alex",
        "program": "Beginner (BG)",
        "weight": 70
    }
    response = client.post('/clients', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['data']['name'] == "Alex"
    assert data['data']['target_calories'] == 70 * 26

def test_register_client_missing_fields(client):
    payload = {"name": "Alex"}
    response = client.post('/clients', json=payload)
    assert response.status_code == 400
    assert b"Name and program are required" in response.data

def test_register_client_invalid_program(client):
    payload = {"name": "Alex", "program": "Advanced (ADV)"}
    response = client.post('/clients', json=payload)
    assert response.status_code == 400
    assert b"Invalid program selected" in response.data