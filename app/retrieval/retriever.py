
from app.ingestion.vector_store import get_chroma_client
from app.ingestion.embedder import load_embedding_model


MODEL_NAME = "all-MiniLM-L6-v2"


def search_documents(
    query,
    collection_name="documents",
    top_k=3
):
    """
    Search ChromaDB for the most relevant document chunks.

    Args:
        query: User's question.
        collection_name: ChromaDB collection name.
        top_k: Number of relevant chunks to retrieve.

    Returns:
        List of matching chunks with their metadata and distances.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    client = get_chroma_client()

    collection = client.get_collection(
        name=collection_name
    )

    total_records = collection.count()

    if total_records == 0:
        return []

    # Load the same embedding model used during ingestion
    model = load_embedding_model(MODEL_NAME)

    # Convert the user's question into an embedding
    query_embedding = model.encode(
        query.strip(),
        convert_to_numpy=True,
        normalize_embeddings=True
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total_records),
        include=["documents", "metadatas", "distances"]
    )

    retrieved_chunks = []

    for i in range(len(results["ids"][0])):
        retrieved_chunks.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved_chunks
