from locust import HttpUser, task, between

class YazLabUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def load_test_request(self):
        # BURAYI HARFİ HARFİNE KONTROL ET
        headers = {
            "Authorization": "Bearer 722d5e14-52ff-4fe5-a323-0cf28a8052a1",
            "Content-Type": "application/json"
        }
        
        payload = {
            "username": "locust_tester",
            "email": "test@kocaeli.edu.tr"
        }
        
        # self.client.post kullanırken headers değişkenini verdiğimizden emin oluyoruz
        with self.client.post("/api/users", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 201 or response.status_code == 200:
                response.success()
            else:
                # Hatanın ne olduğunu terminale de yazdıralım ki görelim
                print(f"Hata Alındı: {response.status_code} - {response.text}")
                response.failure(f"Hata: {response.status_code}")