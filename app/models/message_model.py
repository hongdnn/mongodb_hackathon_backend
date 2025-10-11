from typing import List

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    message: str
    user_id: str
    embedding: List[float]


class MessageCreate(MessageBase):
    """Payload expected when creating a message."""


class MessageInDB(MessageBase):
    id: str = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
