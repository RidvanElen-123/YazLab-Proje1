import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PostService")

class PostModel(BaseModel):
    title: str
    content: str
    author_id: str

class PostServiceApp:
  
    def __init__(self):
        self.app = FastAPI(title="YazLab Post Service")
        self._setup_db()
        self._setup_routes()

    def _setup_db(self):
        # docker-compose.yml içindeki bağımsız mongo-post servisine bağlanır
        self.client = AsyncIOMotorClient("mongodb://mongo-post:27017")
        self.db = self.client.post_database
        self.collection = self.db.posts

    def _setup_routes(self):
        self.app.add_api_route("/posts/", self.create_post, methods=["POST"], status_code=201)
        self.app.add_api_route("/posts/{post_id}", self.get_post, methods=["GET"])
        self.app.add_api_route("/posts/{post_id}", self.update_post, methods=["PUT"])
        self.app.add_api_route("/posts/{post_id}", self.delete_post, methods=["DELETE"], status_code=204)

    async def create_post(self, post: PostModel):
        new_post = await self.collection.insert_one(post.model_dump())
        logger.info(f"Yeni gönderi oluşturuldu: {new_post.inserted_id}")
        return {"id": str(new_post.inserted_id), "message": "Gönderi başarıyla paylaşıldı"}

    async def get_post(self, post_id: str):
        if not ObjectId.is_valid(post_id):
            raise HTTPException(status_code=400, detail="Geçersiz ID formatı")
        
        post = await self.collection.find_one({"_id": ObjectId(post_id)})
        if post:
            post["id"] = str(post["_id"])
            del post["_id"]
            return post
            
        logger.warning(f"Gönderi bulunamadı: {post_id}")
        raise HTTPException(status_code=404, detail="Gönderi bulunamadı")

    async def update_post(self, post_id: str, post_data: PostModel):
        if not ObjectId.is_valid(post_id):
            raise HTTPException(status_code=400, detail="Geçersiz ID formatı")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(post_id)}, {"$set": post_data.model_dump()}
        )
        
        if result.modified_count == 1:
            logger.info(f"Gönderi güncellendi: {post_id}")
            return {"message": "Gönderi başarıyla güncellendi"}
            
        raise HTTPException(status_code=404, detail="Gönderi bulunamadı veya değişiklik yapılmadı")

    async def delete_post(self, post_id: str):
        if not ObjectId.is_valid(post_id):
            raise HTTPException(status_code=400, detail="Geçersiz ID formatı")
            
        result = await self.collection.delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count == 1:
            logger.info(f"Gönderi silindi: {post_id}")
            return 
            
        raise HTTPException(status_code=404, detail="Gönderi bulunamadı")

post_service = PostServiceApp()
app = post_service.app