import logging
import httpx
from fastapi import Request
from fastapi.responses import JSONResponse

# Loglama yapılandırması (İster 3.1: Tüm trafik işlemleri loglanmalı)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ServiceProxy")

class ServiceProxy:
    """
    Mikroservisler arası iletişimi sağlayan ve trafiği yönlendiren proxy sınıfı.
    """
    def __init__(self):
        # follow_redirects=True sayesinde 307 hatalarını arkada sessizce çözer
        self.client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    async def forward(self, url: str, request: Request) -> JSONResponse:
        """
        Gelen isteği hedef URL'e yönlendirir ve sonucu döner.
        """
        logger.info(f"Trafik yönlendiriliyor: {request.method} -> {url}")
        
        try:
            # Header'ları kopyala ama 'host'u temizle (Docker ağında isimler değişir)
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None) # Body yeniden paketleneceği için güvenli

            resp = await self.client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body()
            )
            
            logger.info(f"Hedef servisten yanıt alındı: {url} - Durum Kodu: {resp.status_code}")

            # Hedef servisin cevabı boşsa veya JSON değilse hata almamak için:
            try:
                content = resp.json()
            except ValueError:
                content = {"message": resp.text}

            return JSONResponse(status_code=resp.status_code, content=content)
            
        except httpx.ConnectError:
            logger.error(f"Bağlantı hatası: {url} adresine ulaşılamıyor.")
            # İster 3.1: {"error": true} yapısından kaçınıldı, uygun format ve kod eklendi
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
        """İstemci oturumunu güvenli bir şekilde kapatır."""
        await self.client.aclose()