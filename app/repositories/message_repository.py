from typing import Dict

from app.db import mongo
from app.embedding import embedding_model
from app.models.message_model import MessageCreate, MessageInDB


def insert_message(payload: MessageCreate) -> Dict:
    """
    Insert a message document into the 'messages' collection.
    Returns the inserted document with the generated identifier.
    """
    messages_collection = mongo["messages"]

    # Generate embedding
    embedded_message = embedding_model.generate_message_embedding(payload.message)

    # Create a new MessageInDB instance with embedding
    message_in_db = MessageInDB(
        **payload.dict(),
        embedding=embedded_message,
        id=""  # Placeholder, will be set after insertion
    )

    # Convert to dict (use by_alias=True to ensure _id is correct)
    message_data = message_in_db.dict(by_alias=True, exclude={"id"})
    result = messages_collection.insert_one(message_data)

    # Add the generated ID to the response object
    message_in_db.id = str(result.inserted_id)

    # Return response without embedding
    return message_in_db.dict(exclude={"embedding"})
