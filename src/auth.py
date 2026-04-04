import redis, uuid

class AuthHandler:
    def __init__(self):
        try:
            # NoSQL Izolasyonu: Sadece bu uniteye ozel Redis baglantisi
            self.redis_client = redis.Redis(host='redis-auth', port=6379, db=0, decode_responses=True)
        except:
            self.redis_client = None

    def create_session(self, username: str):
        token = str(uuid.uuid4())
        if self.redis_client:
            self.redis_client.set(f"token:{token}", username, ex=3600)
        return token

    def is_valid(self, token: str):
        if not self.redis_client: return False
        return self.redis_client.exists(f"token:{token}")
