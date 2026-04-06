import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestDispatcherAPI:
   
    
    @classmethod
    def setup_class(cls):
        
       
        cls.client = TestClient(app)

    def test_health_check(self):
      
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_gateway_unauthorized_access(self):
       
        response = self.client.get("/api/users/")
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_invalid_route_returns_404(self):
        
        response = self.client.get("/api/bilinmeyen_rota/")
        assert response.status_code == 404

    def test_post_request_requires_auth(self):
   
        payload = {"title": "Yeni Gönderi Testi", "content": "TDD Test"}
        response = self.client.post("/api/posts/", json=payload)
       
      
        assert response.status_code == 401