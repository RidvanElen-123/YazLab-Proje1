from locust import HttpUser, task, between
import random

class YazLabLoadTest(HttpUser):
    # Her istek arasında 1-3 saniye bekleme (Gerçekçi kullanıcı davranışı)
    wait_time = between(1, 3)

    def on_start(self):
        """Test başlarken her kullanıcı bir kez login olur."""
        response = self.client.post(
            "/api/auth/auth/login", 
            json={"username": "admin", "password": "1234"}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            self.token = None

    @task(4)
    def test_health_check(self):
        """Dispatcher'ın yük altındaki tepki süresini ölçer."""
        self.client.get("/health", name="01 - Gateway Health Check")

    @task(3)
    def test_create_user(self):
        """User Service (MongoDB-User) yazma performansını ölçer."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": f"User_{random.randint(1000, 9999)}", 
                "email": f"test_{random.randint(1000, 9999)}@yazlab.com"
            }
            self.client.post("/api/users/users/", json=payload, headers=headers, name="02 - Create User (POST)")

    @task(2)
    def test_create_post(self):
        """Post Service (MongoDB-Post) yazma performansını ölçer."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "title": f"Yük Testi Başlığı {random.randint(1, 100)}",
                "content": "Bu post otomatik yük testi tarafından oluşturuldu.",
                "author_id": "65f1234567890abcdef12345" # Örnek bir ID
            }
            self.client.post("/api/posts/posts/", json=payload, headers=headers, name="03 - Create Post (POST)")

    @task(1)
    def test_unauthorized_access(self):
        """Güvenlik katmanının (Auth) doğruluğunu denetler."""
        # Token göndermiyoruz, 401 bekliyoruz
        self.client.get("/api/posts/posts/", name="04 - Unauthorized Access Test")