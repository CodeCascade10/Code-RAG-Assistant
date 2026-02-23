from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Load embedding model once (important)
model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_context(query: str, top_k: int = 5) -> str:
    """
    Takes user query → converts to embedding →
    searches Pinecone → returns combined context text.
    """

    # Convert query to embedding
    query_embedding = model.encode(query).tolist()

    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    if not results.get("matches"):
        return ""

    # Extract text from metadata
    contexts = []
    for match in results["matches"]:
        metadata = match.get("metadata", {})
        text = metadata.get("text", "")
        if text:
            contexts.append(text)

    return "\n\n".join(contexts)