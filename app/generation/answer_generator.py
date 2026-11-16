
import ollama


MODEL_NAME = "qwen2.5:3b"


def generate_answer(query, retrieved_chunks):
    """
    Generate an answer using Ollama and retrieved document chunks.
    """

    if not retrieved_chunks:
        return "I couldn't find relevant information in the provided document."

    # Build context from retrieved chunks
    context = ""

    for index, chunk in enumerate(retrieved_chunks, start=1):
        page = chunk["metadata"]["page"]

        context += (
            f"\n[Source {index} | Page {page}]\n"
            f"{chunk['text']}\n"
        )

    prompt = f"""
You are a document assistant.

Answer the user's question using ONLY the information
provided in the document context below.

Rules:
1. Do not use outside knowledge.
2. Do not invent missing information.
3. If the answer is not available in the context,
   clearly say that the document does not provide the answer.
4. If the document contains placeholders, preserve them
   exactly instead of guessing their values.
5. Keep your answer clear and concise.
6. Mention the relevant page number when possible.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content.strip()
