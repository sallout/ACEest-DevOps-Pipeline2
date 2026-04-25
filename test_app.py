import os
import pytest
from app import app, init_db

@pytest.fixture
def client():
    """Setup a test client and an isolated test database."""
    app.config['TESTING'] = True
    
    # Isolate database for tests
    import app as my_app
    original_db = my_app.DB_NAME
    my_app.DB_NAME = "test_aceest.db"
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
        
    # Cleanup after tests
    if os.path.exists("test_aceest.db"):
        os.remove("test_aceest.db")
    my_app.DB_NAME = original_db

def test_health_check(client):
    """Test the readiness probe endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_create_and_get_client(client):
    """Test the core client creation and retrieval flow."""
    payload = {
        "name": "John Doe",
        "age": 28,
        "weight": 80.5,
        "program": "Muscle Gain (MG)",
        "calories": 2800
    }
    
    # Test creation
    post_res = client.post('/api/clients', json=payload)
    assert post_res.status_code == 201
    
    # Prevent duplicate creation
    dup_res = client.post('/api/clients', json=payload)
    assert dup_res.status_code == 409
    
    # Test retrieval
    get_res = client.get('/api/clients')
    assert get_res.status_code == 200
    assert len(get_res.json) == 1
    assert get_res.json[0]["name"] == "John Doe"