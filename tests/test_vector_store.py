
from app.ingestion.pdf_loader import extract_text_from_pdf
from app.ingestion.chunker import split_into_chunks
from app.ingestion.embedder import generate_embeddings
from app.ingestion.vector_store import store_embeddings

pdf_path = "data/sample_documents/sample.pdf"

# Step 1: Extract PDF text
pages = extract_text_from_pdf(pdf_path)

# Step 2: Generate chunks
chunks = split_into_chunks(pages)

# Step 3: Generate embeddings
embeddings = generate_embeddings(chunks)

# Step 4: Store embeddings in ChromaDB
total_stored = store_embeddings(
    chunks=chunks,
    embeddings=embeddings,
    collection_name="documents",
    document_id="sample"
)

print("\nTotal chunks:", len(chunks))
print("Total embeddings:", len(embeddings))
print("Total records in ChromaDB:", total_stored)

print("\nVector storage successful!")
