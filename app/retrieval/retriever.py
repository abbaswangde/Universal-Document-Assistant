
import ollama

from app.ingestion.vector_store import get_chroma_client
from app.ingestion.embedder import load_embedding_model


MODEL_NAME = "all-MiniLM-L6-v2"


def search_documents(
    query,
    collection_name="documents",
    top_k=3,
    document_id=None
):
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    client = get_chroma_client()

    collection = client.get_collection(
        name=collection_name
    )

    if collection.count() == 0:
        return []

    model = load_embedding_model(MODEL_NAME)

    query_embedding = model.encode(
        query.strip(),
        convert_to_numpy=True,
        normalize_embeddings=True
    ).tolist()

    search_options = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, collection.count()),
        "include": ["documents", "metadatas", "distances"]
    }

    # Restrict search to the selected PDF, when provided
    if document_id:
        search_options["where"] = {
            "document_id": document_id
        }

    results = collection.query(**search_options)

    retrieved_chunks = []

    if not results["ids"] or not results["ids"][0]:
        return []

    for i in range(len(results["ids"][0])):
        retrieved_chunks.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved_chunks
