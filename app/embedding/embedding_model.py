import os
from dotenv import load_dotenv
import voyageai
from typing import List, Dict
from app.db import mongo
from app.embedding import embedding_model

# Load environment variables
load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
RERANK_MODEL = "rerank-lite-1"  # or "rerank-1" if you want more accuracy
if not VOYAGE_API_KEY:
    raise RuntimeError("VOYAGE_API_KEY is not set in environment variables")

# Create single client instance — Voyage AI clients are thread-safe
CLIENT = voyageai.Client(api_key=VOYAGE_API_KEY)

# Embedding configuration
MODEL = "voyage-3.5-lite"
INPUT_TYPE = "document"  


def generate_message_embedding(message: str) -> list[float]:
    """
    Generate an embedding vector for a given message string using Voyage AI.
    
    Args:
        message (str): The message to embed.
    
    Returns:
        list[float]: The embedding vector for the message.
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    response = CLIENT.embed(
        model=MODEL,
        input_type=INPUT_TYPE,
        texts=[message]
    )
    return response.embeddings[0]


def search_similar_messages(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for the top N most similar messages to the given query
    across the entire messages collection using MongoDB vector search.
    """
    messages_collection = mongo["messages"]

    # 1. Convert user query into embedding vector
    query_vector = embedding_model.generate_message_embedding(query)

    # 2. (Optional) Dynamically get total doc count to use as numCandidates
    total_docs = messages_collection.estimated_document_count()

    # 3. Build vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "embedding_index",  # must match your MongoDB vector index name
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": total_docs,  # search all records
                "limit": limit if limit <= total_docs else total_docs                # top N most similar
            }
        },
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "message": 1,
                "user_id": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    candidates = list(messages_collection.aggregate(pipeline))

    if not candidates:
        return []

    # 4. Rerank using Voyage AI
    texts = [c["message"] for c in candidates]
    rerank_response = CLIENT.rerank(
        model=RERANK_MODEL,
        query=query,
        documents=texts
    )

    # 5. Attach rerank scores correctly
    reranked = []
    for r in rerank_response.results:
        if r.relevance_score > 0.7:
            candidate = candidates[r.index]
            candidate["relevance_score"] = r.relevance_score
            reranked.append(candidate)

    # 6. Sort by rerank relevance
    reranked.sort(key=lambda x: x["relevance_score"], reverse=True)

    return reranked[:limit]

def rerank_results(query: str, candidates: list[dict]) -> list[dict]:
    texts = [c["message"] for c in candidates]
    response = CLIENT.rerank(
        model=RERANK_MODEL,
        query=query,
        documents=texts
    )

    # response.results is sorted by relevance
    reranked = []
    for result in response.results:
        candidate = candidates[result.index]
        candidate["relevance_score"] = result.score
        reranked.append(candidate)

    # sort high to low by relevance
    reranked.sort(key=lambda x: x["relevance_score"], reverse=True)
    return reranked