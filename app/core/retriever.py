import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def retrieve_context(query: str, top_k: int = 5) -> str:
    """
    Uses Pinecone hosted MiniLM embedding model (384-dim).
    Safe for Render free tier.
    """

    # Generate embedding via Pinecone inference (384-dim)
    embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query],
        parameters={"input_type":"query"}
    )

    query_vector = embedding.data[0].values

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    if not results.get("matches"):
        return ""

    contexts = []
    for match in results["matches"]:
        metadata = match.get("metadata", {})
        text = metadata.get("text", "")
        if text:
            contexts.append(text)

    return "\n\n".join(contexts)