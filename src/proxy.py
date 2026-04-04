import httpx
from fastapi.responses import JSONResponse

class ServiceProxy:
    """Mikroservis yönlendirme ve RMM Seviye 2 yönetimi."""
    async def forward(self, url: str, request):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.request(
                    method=request.method, url=url,
                    headers=dict(request.headers),
                    content=await request.body(), timeout=5.0
                )
                # RMM Seviye 2: Servis yanıtını ve kodunu aynen ilet
                return JSONResponse(status_code=resp.status_code, content=resp.json())
            except Exception:
                # HTTP 502 Hata yönetimi (Dispatcher sorumluluğu)
                return JSONResponse(status_code=502, content={"error": True, "message": "Service Unavailable"})
