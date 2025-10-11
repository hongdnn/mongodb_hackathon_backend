from typing import Dict

from app.db import mongo
from app.models.message_model import MessageCreate


def insert_message(payload: MessageCreate) -> Dict:
    """
    Insert a message document into the 'messages' collection.
    Returns the inserted document with the generated identifier.
    """
    messages_collection = mongo["messages"]
    message_data = payload.dict()
    result = messages_collection.insert_one(message_data)
    message_data["_id"] = str(result.inserted_id)
    return message_data
