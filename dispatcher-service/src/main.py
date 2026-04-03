from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Dispatcher Service")

USER_SERVICE_URL = "http://user-service:8001"
POST_SERVICE_URL = "http://post-service:8002" # Enes'in yeni servisinin adresi

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "dispatcher"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
        
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("Authorization")
        if auth_header != "Bearer gizli-token-123":
            return JSONResponse(
                status_code=401,
                content={"error": True, "message": "Yetkisiz erişim! Geçerli bir token sağlanmadı."}
            )
            
    return await call_next(request)

# User Service Yönlendirmesi
@app.api_route("/api/users", methods=["GET", "POST"])
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_user_service(request: Request, path: str = ""):
    url = f"{USER_SERVICE_URL}/users/{path}".rstrip("/")
    if not path and request.url.path == "/api/users":
        url = f"{USER_SERVICE_URL}/users"

    async with httpx.AsyncClient() as client:
        body = await request.body()
        try:
            response = await client.request(
                method=request.method, url=url, headers={"Content-Type": "application/json"}, content=body
            )
            return JSONResponse(status_code=response.status_code, content=response.json())
        except httpx.RequestError:
            return JSONResponse(status_code=503, content={"error": True, "message": "User Service su an yanit vermiyor."})

# YENİ EKLENEN: Post Service Yönlendirmesi
@app.api_route("/api/posts", methods=["GET", "POST"])
@app.api_route("/api/posts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_post_service(request: Request, path: str = ""):
    url = f"{POST_SERVICE_URL}/posts/{path}".rstrip("/")
    if not path and request.url.path == "/api/posts":
        url = f"{POST_SERVICE_URL}/posts"

    async with httpx.AsyncClient() as client:
        body = await request.body()
        try:
            response = await client.request(
                method=request.method, url=url, headers={"Content-Type": "application/json"}, content=body
            )
            return JSONResponse(status_code=response.status_code, content=response.json())
        except httpx.RequestError:
            return JSONResponse(status_code=503, content={"error": True, "message": "Post Service su an yanit vermiyor."})