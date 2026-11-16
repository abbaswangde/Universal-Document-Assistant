
from app.ingestion.pdf_loader import extract_text_from_pdf
from app.ingestion.chunker import split_into_chunks

pdf_path = "data/sample_documents/sample.pdf"

# Extract PDF text
pages = extract_text_from_pdf(pdf_path)

# Split extracted text into chunks
chunks = split_into_chunks(pages)

print(f"\nTotal pages: {len(pages)}")
print(f"Total chunks: {len(chunks)}")

# Display chunks
for chunk in chunks:
    print(f"\n--- Chunk {chunk['chunk_id']} | Page {chunk['page']} ---")
    print(chunk["text"])

