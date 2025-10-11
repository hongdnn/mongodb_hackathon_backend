from fastapi import FastAPI, HTTPException

from app.repositories.user_repository import get_all_users
from app.repositories.message_repository import insert_message
from app.models.message_model import MessageCreate, MessageInDB
from app.db import mongo

app = FastAPI(title="MongoDB FastAPI Test")

@app.get("/check")
def health():
    try:
        collections = mongo.list_collection_names()
        return {
            "status": "connected",
            "db_name": mongo.name,
            "collections": collections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/users")
def list_users():
    try:
        users = get_all_users()
        return {"count": len(users), "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages", response_model=MessageInDB)
def create_message(message: MessageCreate):
    try:
        inserted_message = insert_message(message)
        return inserted_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
