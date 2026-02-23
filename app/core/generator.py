from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(context: str, question: str) -> str:
    """
    Sends retrieved context + question to Groq LLM
    """

    if not context.strip():
        return "I couldn't find relevant information in the knowledge base."

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional programming assistant.\n"
                "Only answer programming-related questions.\n"
                "Use the provided context to answer accurately.\n"
                "If the answer is not found in the context, say:\n"
                "'I couldn't find the answer in the knowledge base.'"
            )
        },
        {
            "role": "user",
            "content": f"""
Context:
{context}

Question:
{question}
"""
        }
    ]

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.1,
        max_tokens=700
    )

    return completion.choices[0].message.content.strip()