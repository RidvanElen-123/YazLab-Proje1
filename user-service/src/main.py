import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("UserService")

class UserModel(BaseModel):
    name: str
    email: str
    role: str = "user"

class UserServiceApp:
    """
    Kullanıcı işlemlerini (CRUD) yürüten bağımsız mikroservis sınıfı.
    OOP prensiplerine ve RMM Seviye 2 standartlarına uygun tasarlanmıştır.
    """
    def __init__(self):
        self.app = FastAPI(title="YazLab User Service")
        self._setup_db()
        self._setup_routes()

    def _setup_db(self):
        
        self.client = AsyncIOMotorClient("mongodb://mongo-user:27017")
        self.db = self.client.user_database
        self.collection = self.db.users

    def _setup_routes(self):
        
        self.app.add_api_route("/users/", self.create_user, methods=["POST"], status_code=201)
        self.app.add_api_route("/users/{user_id}", self.get_user, methods=["GET"])
        self.app.add_api_route("/users/{user_id}", self.update_user, methods=["PUT"])
        self.app.add_api_route("/users/{user_id}", self.delete_user, methods=["DELETE"], status_code=204)

    async def create_user(self, user: UserModel):
        """Yeni bir kullanıcı oluşturur (POST)."""
        new_user = await self.collection.insert_one(user.model_dump())
        logger.info(f"Yeni kullanıcı oluşturuldu: {new_user.inserted_id}")
        return {"id": str(new_user.inserted_id), "message": "Kullanıcı başarıyla oluşturuldu"}

    async def get_user(self, user_id: str):
        """Belirli bir kullanıcıyı getirir (GET)."""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Geçersiz ID formatı")
        
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["id"] = str(user["_id"])
            del user["_id"]
            return user
            
        logger.warning(f"Kullanıcı bulunamadı: {user_id}")
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    async def update_user(self, user_id: str, user_data: UserModel):
        """Kullanıcı bilgilerini günceller (PUT)."""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Geçersiz ID formatı")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": user_data.model_dump()}
        )
        
        if result.modified_count == 1:
            logger.info(f"Kullanıcı güncellendi: {user_id}")
            return {"message": "Kullanıcı başarıyla güncellendi"}
            
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı veya değişiklik yapılmadı")

    async def delete_user(self, user_id: str):
        """Kullanıcıyı sistemden siler (DELETE)."""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Geçersiz ID formatı")
            
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 1:
            logger.info(f"Kullanıcı silindi: {user_id}")
            return # HTTP 204 döner
            
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")


user_service = UserServiceApp()
app = user_service.app