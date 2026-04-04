from fastapi import FastAPI, Request, HTTPException
# from .auth_validator import AuthValidator # Token doğrulama işlemi için ayrı bir sınıf olmalı
from .proxy import ServiceProxy

class DispatcherApp:
    """
    API Gateway (Dispatcher) uygulamasını kapsayan ana sınıf.
    Sistemdeki trafik yönlendirmesini ve merkezi yetki kontrolünü sağlar.
    """
    def __init__(self):
        self.app = FastAPI(title="YazLab Dispatcher API Gateway")
        self.proxy = ServiceProxy()
        # self.auth_validator = AuthValidator() 
        self._setup_routes()

    def _setup_routes(self):
        """Uygulama rotalarını FastAPI instance'ına bağlar."""
        self.app.add_api_route("/health", self.health_check, methods=["GET"])
        self.app.add_api_route("/api/{service}/{path:path}", self.gateway_route, methods=["GET", "POST", "PUT", "DELETE"])

    async def health_check(self):
        """Sistemin ayakta olup olmadığını kontrol eden uç nokta."""
        return {"status": "ok", "service": "dispatcher"}

    async def gateway_route(self, request: Request, service: str, path: str = ""):
        """
        Gelen istekleri doğrular ve ilgili mikroservise proxy'ler.
        """
        # 1. Rota ve Servis Eşleştirme (Bağımsız Auth servisi eklendi)
        service_map = {
            "users": ("user-service", 8001), 
            "posts": ("post-service", 8002),
            "auth": ("auth-service", 8003) 
        }
        
        if service not in service_map:
            raise HTTPException(status_code=404, detail="Servis bulunamadı")

        service_name, port = service_map[service]

        # 2. Yetkilendirme Kontrolü (Auth servisine giden login vb. istekler hariç)
        if service != "auth":
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Yetkisiz erişim: Token eksik")
            
            token = auth_header.split(" ")[1]
            
            # TODO: Token doğrulama OOP mantığıyla AuthValidator sınıfı üzerinden yapılmalı
            # if not self.auth_validator.is_valid(token):
            #     raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş session")

        # 3. URL Kurgusu (RMM Seviye 2: Kaynak bazlı URI)
        clean_path = path.strip("/")
        target_url = f"http://{service_name}:{port}/"
        if clean_path:
            target_url += f"{clean_path}/"

        # 4. Proxy üzerinden isteği ilet
        return await self.proxy.forward(target_url, request)

# FastAPI sunucusunun çalıştırabilmesi için sınıfın örneklendirilmesi
dispatcher = DispatcherApp()
app = dispatcher.app