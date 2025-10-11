from typing import List, Dict
from app.db import mongo  

def get_all_users() -> List[Dict]:
    """
    Query all users from the 'users' collection.
    Returns:
        List[Dict]: List of user documents.
    """
    users_collection = mongo["users"]
    users_cursor = users_collection.find({}) 
    users = list(users_cursor)

    for user in users:
        user["_id"] = str(user["_id"])
    return users