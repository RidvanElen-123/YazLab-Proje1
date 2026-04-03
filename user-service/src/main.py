from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI(title="User Service")

# MongoDB Bağlantısı (Docker compose içindeki ağ adını kullanıyoruz)
client = AsyncIOMotorClient("mongodb://mongodb:27017")
db = client.user_database
users_collection = db.users

class User(BaseModel):
    username: str
    email: str

@app.post("/users", status_code=201)
async def create_user(user: User):
    """Yeni kullanıcı oluşturur (RMM: POST)"""
    new_user = await users_collection.insert_one(user.model_dump())
    return {"id": str(new_user.inserted_id), **user.model_dump()}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Kullanıcıyı getirir (RMM: GET ve URI)"""
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
        return user
    raise HTTPException(status_code=404, detail="Kullanici bulunamadi")