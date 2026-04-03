import pytest
from fastapi.testclient import TestClient

try:
    from src.main import app
    client = TestClient(app)
except ModuleNotFoundError:
    client = None

def test_health_check():
    """Dispatcher'ın ayakta olup olmadığını kontrol eder."""
    if not client:
        pytest.fail("src.main modülü ve app nesnesi henüz oluşturulmadı!")
        
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dispatcher"}

def test_unauthorized_request_returns_401():
    """Yetkisiz isteklerin yakalanıp HTTP 401 dönmesini test eder."""
    if not client:
        pytest.fail("src.main modülü ve app nesnesi henüz oluşturulmadı!")
        
    response = client.get("/api/users")
    assert response.status_code == 401
    assert "error" in response.json()