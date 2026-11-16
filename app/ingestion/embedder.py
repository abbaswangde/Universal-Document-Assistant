
from sentence_transformers import SentenceTransformer
from functools import lru_cache

# Default embedding model
MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=2)
def load_embedding_model(model_name=MODEL_NAME):
    """
    Load and cache the Sentence Transformer model.
    """
    print(f"Loading embedding model: {model_name}")

    model = SentenceTransformer(model_name)

    print("Embedding model loaded successfully!")

    return model


def generate_embeddings(chunks, model_name=MODEL_NAME):
    """
    Convert text chunks into numerical embeddings.

    Args:
        chunks: List of dictionaries containing chunk text.
        model_name: Sentence Transformer model name.

    Returns:
        List of numerical embedding vectors.
    """

    if not chunks:
        return []

    texts = [chunk["text"].strip() for chunk in chunks]

    if any(not text for text in texts):
        raise ValueError("One or more chunks contain empty text.")

    model = load_embedding_model(model_name)

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings.tolist()
