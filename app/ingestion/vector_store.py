
import json
import chromadb


def get_chroma_client(persist_directory="data/chroma_db"):
    """
    Create a persistent ChromaDB client.
    """
    return chromadb.PersistentClient(path=persist_directory)


def prepare_metadata(chunk, document_id):
    """
    Prepare chunk metadata for ChromaDB.

    ChromaDB supports string, integer, float and boolean
    metadata values. Complex values are converted to JSON strings.
    """

    metadata = {
        "document_id": str(document_id),
        "chunk_id": int(chunk["chunk_id"])
    }

    for key, value in chunk.items():

        if key in ("text", "chunk_id"):
            continue

        if value is None:
            continue

        if isinstance(value, (str, int, float, bool)):
            metadata[key] = value

        else:
            metadata[key] = json.dumps(
                value,
                ensure_ascii=False,
                default=str
            )

    return metadata


def store_embeddings(
    chunks,
    embeddings,
    collection_name="documents",
    document_id="sample",
    persist_directory="data/chroma_db"
):
    """
    Store document chunks and their embeddings in ChromaDB.

    Preserves metadata from all supported document formats.
    """

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count do not match.")

    if not chunks:
        return 0

    client = get_chroma_client(persist_directory)

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
        prepare_metadata(chunk, document_id)
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return collection.count()
