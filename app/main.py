from fastapi import FastAPI, HTTPException

from app.repositories.user_repository import get_all_users
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