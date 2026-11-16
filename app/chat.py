
from pathlib import Path

from app.ingestion.pdf_loader import extract_text_from_pdf
from app.ingestion.chunker import split_into_chunks
from app.ingestion.embedder import generate_embeddings
from app.ingestion.vector_store import store_embeddings

from app.retrieval.retriever import search_documents
from app.generation.answer_generator import generate_answer


COLLECTION_NAME = "documents"


def upload_document():

    print("\n" + "=" * 50)
    print("          UPLOAD YOUR PDF DOCUMENT")
    print("=" * 50)

    pdf_path = input("\nEnter PDF file path: ").strip()

    # Support paths pasted with surrounding quotes
    pdf_path = pdf_path.strip('"').strip("'")

    if not pdf_path:
        print("No file path provided.")
        return None

    file_path = Path(pdf_path).expanduser()

    if not file_path.exists() or not file_path.is_file():
        print("\nError: File not found.")
        return None

    if file_path.suffix.lower() != ".pdf":
        print("\nError: Please upload a PDF file.")
        return None

    document_id = file_path.stem

    try:
        print("\n[1/4] Extracting PDF text...")

        pages = extract_text_from_pdf(str(file_path))

        if not pages:
            print("No text could be extracted from this PDF.")
            return None

        print(f"Extracted {len(pages)} pages.")

        print("\n[2/4] Splitting text into chunks...")

        chunks = split_into_chunks(pages)

        if not chunks:
            print("No text chunks were generated.")
            return None

        print(f"Generated {len(chunks)} chunks.")

        print("\n[3/4] Generating embeddings...")

        embeddings = generate_embeddings(chunks)

        print(f"Generated {len(embeddings)} embeddings.")

        print("\n[4/4] Storing document in ChromaDB...")

        total_stored = store_embeddings(
            chunks=chunks,
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            document_id=document_id
        )

        print("\nDocument uploaded and processed successfully!")
        print("Document:", file_path.name)
        print("Pages:", len(pages))
        print("Chunks:", len(chunks))
        print("Records in collection:", total_stored)

        return document_id, file_path.name

    except Exception as error:
        print(f"\nDocument processing failed: {error}")
        return None


def start_chat(document_id, document_name):

    print("\n" + "=" * 50)
    print("       UNIVERSAL DOCUMENT ASSISTANT")
    print("=" * 50)

    print(f"\nDocument loaded: {document_name}")
    print("Ask questions about your document.")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:

        try:
            query = input("You: ").strip()

            if query.lower() in ["exit", "quit"]:
                print("\nGoodbye!")
                break

            if not query:
                continue

            retrieved_chunks = search_documents(
                query=query,
                collection_name=COLLECTION_NAME,
                top_k=3,
                document_id=document_id
            )

            answer = generate_answer(
                query=query,
                retrieved_chunks=retrieved_chunks
            )

            print("\nAssistant:", answer)
            print("\n" + "-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n\nChat ended. Goodbye!")
            break

        except Exception as error:
            print(f"\nAn error occurred: {error}\n")


if __name__ == "__main__":

    document_info = upload_document()

    if document_info:
        document_id, document_name = document_info

        start_chat(
            document_id=document_id,
            document_name=document_name
        )
