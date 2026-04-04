import pytest
from fastapi.testclient import TestClient

try:
    from src.main import app
    client = TestClient(app)
except ModuleNotFoundError:
    client = None

def test_health_check():
    """TDD Red Phase: Kod henüz yoksa test başarısız olmalı."""
    if not client: pytest.fail("Kod henüz hazır değil!")
    response = client.get("/health")
    assert response.status_code == 200

def test_unauthorized_401():
    """Yetkisiz erişimin 401 dönmesini denetler."""
    if not client: pytest.fail("Kod henüz hazır değil!")
    response = client.get("/api/users")
    assert response.status_code == 401
