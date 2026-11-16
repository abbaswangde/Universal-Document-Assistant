
from app.ingestion.pdf_loader import extract_text_from_pdf
from app.ingestion.chunker import split_into_chunks
from app.ingestion.embedder import generate_embeddings

pdf_path = "data/sample_documents/sample.pdf"

# Step 1: Extract PDF text
pages = extract_text_from_pdf(pdf_path)

# Step 2: Generate chunks
chunks = split_into_chunks(pages)

# Step 3: Generate embeddings
embeddings = generate_embeddings(chunks)

# Step 4: Display results
print("\nTotal chunks:", len(chunks))
print("Total embeddings:", len(embeddings))

if embeddings:
    print("Embedding dimensions:", len(embeddings[0]))
    print("\nFirst embedding:")
    print(embeddings[0][:10])
