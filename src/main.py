from fastapi import FastAPI, Request
from .auth import AuthHandler
from .proxy import ServiceProxy

app = FastAPI(title="YazLab Gateway")
auth = AuthHandler()
proxy = ServiceProxy()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "dispatcher"}

@app.post("/login")
async def login(username: str):
    token = auth.create_session(username)
    return {"access_token": token, "token_type": "bearer"}

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(request: Request, service: str, path: str = ""):
    # URL yapısı üzerinden kaynak tanımlama (RMM Seviye 2)
    port = 8001 if service == "users" else 8002
    target_url = f"http://{service}-service:{port}/{service}/{path}"
    return await proxy.forward(target_url, request)
