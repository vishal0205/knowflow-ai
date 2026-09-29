import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = "gemini-3.5-flash-lite"


def generate_answer(question: str, context: str) -> str:

    prompt = f"""
You are KnowFlow AI, an enterprise knowledge assistant.

Answer the user's question using ONLY the provided context.

Citation rules:
1. Every factual statement must have a citation.
2. Use the citation IDs provided in the context, such as [1] or [2].
3. Put citations immediately after the statement they support.
4. Never invent citation IDs.
5. Do not cite information that is not present in the context.

Grounding rules:
1. Do not use outside knowledge.
2. Do not invent or assume information.
3. If the answer cannot be found in the context, say:
   "I don't have enough information in the provided documents to answer that."
4. Keep the answer concise and factual.

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text