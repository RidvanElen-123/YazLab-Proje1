from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Dispatcher Service")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "dispatcher"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=401,
            content={"error": True, "message": "Yetkisiz erişim!"}
        )
    return await call_next(request)