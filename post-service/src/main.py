from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI(title="Post Service")

# MongoDB Bağlantısı (User Service'ten bağımsız bir veri tabanı tablosu)
client = AsyncIOMotorClient("mongodb://mongodb:27017")
db = client.post_database
posts_collection = db.posts

class Post(BaseModel):
    user_id: str
    content: str

@app.post("/posts", status_code=201)
async def create_post(post: Post):
    """Yeni gönderi oluşturur (RMM: POST)"""
    new_post = await posts_collection.insert_one(post.model_dump())
    return {"id": str(new_post.inserted_id), **post.model_dump()}

@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    """Belirli bir gönderiyi getirir (RMM: GET)"""
    post = await posts_collection.find_one({"_id": ObjectId(post_id)})
    if post:
        post["id"] = str(post["_id"])
        del post["_id"]
        return post
    raise HTTPException(status_code=404, detail="Gonderi bulunamadi")