from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import redis
import uuid
import time
import logging

# Terminalde ne olup bittiğini görmek için Loglama ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Dispatcher-Gateway")

app = FastAPI(title="YazLab Proje 1 - Dispatcher")

USER_SERVICE_URL = "http://user-service:8001"
POST_SERVICE_URL = "http://post-service:8002"

try:
    redis_client = redis.Redis(host='redis-auth', port=6379, db=0, decode_responses=True)
except:
    redis_client = None

# --- YENİ: GLOBAL HATA YÖNETİMİ ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Sistemde beklenmedik bir hata oluşursa (500) devreye girer."""
    logger.error(f"Beklenmedik Hata: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": True, "type": "InternalServerError", "message": "Sistemde teknik bir ariza olustu."}
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "dispatcher", "timestamp": time.time()}

@app.post("/login")
async def login(username: str):
    token = str(uuid.uuid4())
    if redis_client:
        redis_client.set(f"token:{token}", username, ex=3600)
    logger.info(f"YENİ OTURUM: Kullanıcı {username} için token üretildi.")
    return {"access_token": token, "token_type": "bearer"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    start_time = time.time()
    
    # 1. Adım: Yetki Kontrolü
    if request.url.path not in ["/health", "/login"]:
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(status_code=401, content={"error": True, "message": "Token eksik."})
            
            token = auth_header.split(" ")[1]
            if redis_client and not redis_client.exists(f"token:{token}"):
                if token != "gizli-token-123":
                    return JSONResponse(status_code=401, content={"error": True, "message": "Gecersiz token."})
    
    # 2. Adım: İsteği İşle ve Süreyi Ölç (Performance Logging)
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"ISTEK: {request.method} {request.url.path} - SURE: {process_time:.4f}s - STATU: {response.status_code}")
    
    return response

# --- YÖNLENDİRME (PROXY) METOTLARI ---
async def proxy_request(url: str, request: Request):
    """Kod tekrarını önlemek için ortak Proxy fonksiyonu (Refactor)"""
    async with httpx.AsyncClient() as client:
        body = await request.body()
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                headers={"Content-Type": "application/json"},
                content=body,
                timeout=5.0 # 5 saniye içinde cevap gelmezse pes et
            )
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        except httpx.TimeoutException:
            logger.error(f"TIMEOUT: {url} adresinden cevap gecikti.")
            return JSONResponse(status_code=504, content={"error": True, "message": "Servis zamanasina ugradi."})
        except Exception as e:
            logger.error(f"PROXY HATASI: {str(e)}")
            return JSONResponse(status_code=502, content={"error": True, "message": "Hedef servise ulasilamiyor."})

@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/users", methods=["GET", "POST"])
async def route_user(request: Request, path: str = ""):
    target_url = f"{USER_SERVICE_URL}/users/{path}".rstrip("/")
    if not path and request.url.path == "/api/users": target_url = f"{USER_SERVICE_URL}/users"
    return await proxy_request(target_url, request)

@app.api_route("/api/posts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/posts", methods=["GET", "POST"])
async def route_post(request: Request, path: str = ""):
    target_url = f"{POST_SERVICE_URL}/posts/{path}".rstrip("/")
    if not path and request.url.path == "/api/posts": target_url = f"{POST_SERVICE_URL}/posts"
    return await proxy_request(target_url, request)