import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestDispatcherAPI:
    """
    Dispatcher servisinin davranışlarını OOP prensiplerine uygun 
    olarak test eden sınıf.
    """
    
    @classmethod
    def setup_class(cls):
        # Test istemcisi sınıf başlatıldığında bir kez oluşturulur
        cls.client = TestClient(app)

    def test_health_check(self):
        """Dispatcher'ın ayakta olup olmadığını kontrol eder."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_gateway_unauthorized_access(self):
        """Yetkilendirme (Token) olmadan mikroservise erişim engellenmelidir."""
        response = self.client.get("/api/users/")
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_invalid_route_returns_404(self):
        """Sistemde tanımlı olmayan bir URL rotasına istek atıldığında HTTP 404 dönmelidir."""
        response = self.client.get("/api/bilinmeyen_rota/")
        assert response.status_code == 404

    def test_post_request_requires_auth(self):
        """RMM standartlarına uygun POST işlemlerinde de yetki kontrolü yapılmalıdır."""
        payload = {"title": "Yeni Gönderi Testi", "content": "TDD Test"}
        response = self.client.post("/api/posts/", json=payload)
        # Token olmadığı için 401 dönmesini bekliyoruz
        assert response.status_code == 401