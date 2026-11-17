
from app.ingestion.vector_store import get_chroma_client
from app.ingestion.embedder import load_embedding_model


MODEL_NAME = "all-MiniLM-L6-v2"


def search_documents(
    query,
    collection_name="documents",
    top_k=3,
    document_id=None,
    persist_directory="data/chroma_db"
):
    """
    Search for relevant document chunks using semantic similarity.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    client = get_chroma_client(persist_directory)

    try:
        collection = client.get_collection(name=collection_name)
    except Exception as error:
        raise ValueError(
            f"Collection '{collection_name}' does not exist."
        ) from error

    total_count = collection.count()

    if total_count == 0:
        return []

    model = load_embedding_model(MODEL_NAME)

    query_embedding = model.encode(
        query.strip(),
        convert_to_numpy=True,
        normalize_embeddings=True
    ).tolist()

    search_options = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, total_count),
        "include": ["documents", "metadatas", "distances"]
    }

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
