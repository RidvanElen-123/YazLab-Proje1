import logging
import httpx
from fastapi import Request
from fastapi.responses import JSONResponse


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ServiceProxy")

class ServiceProxy:
  
    def __init__(self):
        
      
        self.client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    async def forward(self, url: str, request: Request) -> JSONResponse:
        
       
        logger.info(f"Trafik yönlendiriliyor: {request.method} -> {url}")
        
        try:
            
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None) 
          
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)

            resp = await self.client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body()
            )
            
            logger.info(f"Hedef servisten yanıt alındı: {url} - Durum Kodu: {resp.status_code}")

            
          
            try:
                content = resp.json()
            except ValueError:
                content = {"message": resp.text}

            return JSONResponse(status_code=resp.status_code, content=content)
            
        except httpx.ConnectError:
            logger.error(f"Bağlantı hatası: {url} adresine ulaşılamıyor.")
            
           
            return JSONResponse(
                status_code=503, 
                content={"message": "Service Unavailable", "detail": "Hedef servise şu anda ulaşılamıyor."}
            )
        except Exception as e:
            logger.error(f"Beklenmeyen hata ({url}): {str(e)}")
            return JSONResponse(
                status_code=502, 
                content={"message": "Bad Gateway", "detail": "Sunucu içi proxy yönlendirme hatası oluştu."}
            )

    async def close(self):
       
        await self.client.aclose()