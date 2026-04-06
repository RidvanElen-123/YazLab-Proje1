import logging
import uuid
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AuthService")

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthApp:

    def __init__(self):
        self.app = FastAPI(title="YazLab Auth Service")
    
        self.redis_client = redis.Redis(host='redis-auth', port=6379, db=0, decode_responses=True)
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_api_route("/auth/login", self.login, methods=["POST"])
        self.app.add_api_route("/auth/validate", self.validate_token, methods=["GET"])

    async def login(self, request: LoginRequest):
       
  
        if request.username == "admin" and request.password == "1234":
            token = str(uuid.uuid4())
          
            self.redis_client.setex(f"session:{token}", 3600, request.username)
            logger.info(f"Kullanıcı girişi başarılı: {request.username}")
            return {"access_token": token, "token_type": "bearer"}
        
        logger.warning(f"Başarısız giriş denemesi: {request.username}")
       
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")

    async def validate_token(self, token: str):
       
        username = self.redis_client.get(f"session:{token}")
        if username:
            return {"valid": True, "username": username}
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token")


auth_service = AuthApp()
app = auth_service.app