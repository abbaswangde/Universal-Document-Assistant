
from pathlib import Path

from app.ingestion.loaders.document_loader import load_document
from app.ingestion.chunker import split_into_chunks
from app.ingestion.embedder import generate_embeddings
from app.ingestion.vector_store import store_embeddings

from app.retrieval.retriever import search_documents
from app.generation.answer_generator import generate_answer


COLLECTION_NAME = "documents"


def upload_document():

    print("\n" + "=" * 55)
    print("          UNIVERSAL DOCUMENT ASSISTANT")
    print("=" * 55)

    print("\nSupported formats:")
    print("PDF, DOCX, XLSX, PPTX, TXT, MD, CSV, JSON, HTML")
    print("PNG, JPG, JPEG, TIFF, BMP")
    print("Legacy: DOC, XLS, PPT (requires LibreOffice)")

    file_path = input("\nEnter document file path: ").strip()

    # Support paths pasted with surrounding quotes.
    file_path = file_path.strip('"').strip("'")

    if not file_path:
        print("\nNo file path provided.")
        return None

    file_path = Path(file_path).expanduser()

    if not file_path.exists() or not file_path.is_file():
        print("\nError: File not found.")
        return None

    try:

        print("\n[1/4] Extracting document content...")

        document = load_document(file_path)

        records = document["content"]

        if not records:
            print("No content could be extracted from this document.")
            return None

        # Ensure every record has basic source information.
        for record in records:
            record.setdefault("source", document["filename"])
            record.setdefault(
                "source_type",
                document["file_type"].lstrip(".")
            )

        print("Document:", document["filename"])
        print("File type:", document["file_type"])
        print("Extracted characters:", document["character_count"])
        print("Extracted records:", len(records))

        print("\n[2/4] Splitting content into chunks...")

        chunks = split_into_chunks(records)

        if not chunks:
            print("No text chunks were generated.")
            return None

        print("Generated chunks:", len(chunks))

        print("\n[3/4] Generating embeddings...")

        embeddings = generate_embeddings(chunks)

        print("Generated embeddings:", len(embeddings))

        print("\n[4/4] Storing document in ChromaDB...")

        # Keep the existing document ID convention.
        document_id = file_path.stem

        total_stored = store_embeddings(
            chunks=chunks,
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            document_id=document_id
        )

        print("\n" + "=" * 55)
        print("       DOCUMENT PROCESSED SUCCESSFULLY!")
        print("=" * 55)

        print("Filename:", document["filename"])
        print("Document ID:", document_id)
        print("File type:", document["file_type"])
        print("Records:", len(records))
        print("Chunks:", len(chunks))
        print("Total records in collection:", total_stored)

        return document_id, document["filename"]

    except Exception as error:

        print("\nDocument processing failed:")
        print(error)

        return None


def start_chat(document_id, document_name):

    print("\n" + "=" * 55)
    print("             DOCUMENT CHAT")
    print("=" * 55)

    print("\nDocument loaded:", document_name)
    print("\nAsk questions about your document.")
    print("Type 'exit' or 'quit' to end the conversation.")

    while True:

        try:

            query = input("\nYou: ").strip()

            if query.lower() in ("exit", "quit"):
                print("\nGoodbye!")
                break

            if not query:
                continue

            print("\nSearching document...")

            retrieved_chunks = search_documents(
                query=query,
                collection_name=COLLECTION_NAME,
                top_k=3,
                document_id=document_id
            )

            if not retrieved_chunks:
                print(
                    "\nAssistant: I couldn't find relevant "
                    "information in this document."
                )
                continue

            answer = generate_answer(
                query=query,
                retrieved_chunks=retrieved_chunks
            )

            print("\nAssistant:", answer)

            print("\n" + "-" * 55)

        except KeyboardInterrupt:
            print("\n\nChat ended. Goodbye!")
            break

        except Exception as error:
            print("\nAn error occurred:", error)


def main():

    document_info = upload_document()

    if document_info:

        document_id, document_name = document_info

        start_chat(
            document_id=document_id,
            document_name=document_name
        )


if __name__ == "__main__":
    main()
