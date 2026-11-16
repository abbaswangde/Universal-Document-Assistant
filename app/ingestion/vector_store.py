
import chromadb


def get_chroma_client(persist_directory="data/chroma_db"):
    """
    Create a persistent ChromaDB client.
    """
    return chromadb.PersistentClient(path=persist_directory)


def store_embeddings(
    chunks,
    embeddings,
    collection_name="documents",
    document_id="sample"
):
    """
    Store document chunks and their embeddings in ChromaDB.
    """

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count do not match.")

    if not chunks:
        return 0

    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    ids = [
        f"{document_id}_{chunk['chunk_id']}"
        for chunk in chunks
    ]

    documents = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "document_id": document_id,
            "chunk_id": int(chunk["chunk_id"]),
            "page": int(chunk["page"])
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return collection.count()
