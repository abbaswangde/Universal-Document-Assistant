
import ollama


MODEL_NAME = "qwen2.5:3b"


def format_source_location(metadata):
    """
    Build a readable source location from available metadata.
    Supports PDF, Word, Excel, PowerPoint and text documents.
    """

    locations = []

    if metadata.get("page") is not None:
        locations.append(f"Page {metadata['page']}")

    if metadata.get("sheet"):
        locations.append(f"Sheet: {metadata['sheet']}")

    if metadata.get("slide") is not None:
        locations.append(f"Slide {metadata['slide']}")

    if metadata.get("section"):
        locations.append(f"Section: {metadata['section']}")

    source = metadata.get("source", "Unknown document")

    location = " | ".join(locations)

    if location:
        return f"{source} | {location}"

    return source


def generate_answer(query, retrieved_chunks):
    """
    Generate an answer using Ollama and retrieved document chunks.
    Source metadata is included in the context.
    """

    if not retrieved_chunks:
        return (
            "I couldn't find relevant information "
            "in the provided document."
        )

    context_parts = []

    for index, chunk in enumerate(retrieved_chunks, start=1):

        metadata = chunk.get("metadata", {})

        source_location = format_source_location(metadata)

        context_parts.append(
            f"\n[Source {index} | {source_location}]\n"
            f"{chunk['text']}\n"
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a universal document assistant.

Answer the user's question using ONLY the information
provided in the document context below.

Rules:
1. Do not use outside knowledge.
2. Do not invent missing information.
3. If the answer is unavailable, clearly say so.
4. Preserve document placeholders exactly.
5. Keep your answer clear and concise.
6. Mention the relevant source location when possible.

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
