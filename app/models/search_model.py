from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = 10