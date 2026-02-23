from .retriever import retrieve_context
from .generator import generate_answer
from .guard import is_code_related


def handle_query(query: str) -> str:
    """
    Full RAG pipeline:
    Guard → Retrieve → Generate
    """

    # 1️⃣ Guard layer
    if not is_code_related(query):
        return "I only answer programming related questions."

    # 2️⃣ Retrieve context
    context = retrieve_context(query)

    if not context:
        return "I couldn't find relevant information in the knowledge base."

    # 3️⃣ Generate answer using Groq
    answer = generate_answer(context, query)

    return answer