from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Dispatcher Service")

# Docker ağındaki user-service'in dahili adresi
USER_SERVICE_URL = "http://user-service:8001"

@app.get("/health")
async def health_check():
    """Testlerin geçmesi için Health Check endpointi."""
    return {"status": "ok", "service": "dispatcher"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Yetki Kontrolü (Auth) Katmanı"""
    if request.url.path == "/health":
        return await call_next(request)
        
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("Authorization")
        # Basit token kontrolü (TDD testimiz header göndermediği için 401 dönmeye devam edecek)
        # İlerleyen aşamada burayı Redis'e bağlayacağız.
        if auth_header != "Bearer gizli-token-123":
            return JSONResponse(
                status_code=401,
                content={"error": True, "message": "Yetkisiz erişim! Geçerli bir token sağlanmadı."}
            )
            
    return await call_next(request)

@app.api_route("/api/users", methods=["GET", "POST"])
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_user_service(request: Request, path: str = ""):
    """Gelen istekleri User Service'e yönlendiren Proxy metodu [cite: 39, 47]"""
    
    # user-service'in RMM standartlarına uygun URL'sini oluşturuyoruz [cite: 58, 59]
    url = f"{USER_SERVICE_URL}/users/{path}".rstrip("/")
    if not path and request.url.path == "/api/users":
        url = f"{USER_SERVICE_URL}/users"

    async with httpx.AsyncClient() as client:
        body = await request.body()
        try:
            # İsteği iç ağdaki servise fırlat ve cevabı bekle
            response = await client.request(
                method=request.method,
                url=url,
                headers={"Content-Type": "application/json"},
                content=body
            )
            return JSONResponse(status_code=response.status_code, content=response.json())
        except httpx.RequestError:
            # Eğer user-service çökerse, sisteme uygun hata kodunu dön (HTTP 5xx kuralı) [cite: 41]
            return JSONResponse(
                status_code=503,
                content={"error": True, "message": "User Service su an yanit vermiyor."}
            )