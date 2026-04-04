from locust import HttpUser, task, between
import random

class YazLabLoadTest(HttpUser):
    # Her istek arasında 1 ile 3 saniye arası rastgele bekleme süresi
    wait_time = between(1, 3)

    def on_start(self):
        """Her simüle edilen kullanıcı testi başlatırken önce login olup token alır."""
        response = self.client.post(
            "/api/auth/auth/login", 
            json={"username": "admin", "password": "1234"}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            self.token = None

    @task(3)
    def test_health_check(self):
        """Sistemin ayakta olup olmadığını kontrol eden yoğun test."""
        self.client.get("/health", name="Dispatcher Health Check")

    @task(2)
    def test_create_user(self):
        """Dispatcher üzerinden User servisine veri yazma testi (POST)."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": f"Test User {random.randint(1, 1000)}", 
                "email": f"test{random.randint(1, 1000)}@mail.com"
            }
            self.client.post("/api/users/users/", json=payload, headers=headers, name="Create User via Gateway")

    @task(1)
    def test_unauthorized_access(self):
        """Token olmadan mikroservislere erişmeye çalışma (401 dönmeli)."""
        self.client.get("/api/posts/posts/", name="Unauthorized Post Access")