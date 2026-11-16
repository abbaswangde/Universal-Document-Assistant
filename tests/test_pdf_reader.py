
from app.ingestion.pdf_loader import extract_text_from_pdf

pdf_path = "data/sample_documents/sample.pdf"

pages = extract_text_from_pdf(pdf_path)

for page in pages:
    print(f"\n--- Page {page['page']} ---")
    print(page["text"])
