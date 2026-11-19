from pathlib import Path
import pymupdf

from app.ingestion.loaders.text_parser import create_record


def parse_pdf(file_path):
    """
    Extract text from PDF documents using PyMuPDF.

    Returns one standardized record per non-empty page.
    Preserves page numbers and source metadata.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Unsupported file format: {file_path.suffix}"
        )

    records = []

    try:
        with pymupdf.open(file_path) as document:

            for page_number, page in enumerate(document, start=1):

                page_text = page.get_text("text").strip()

                if page_text:
                    record = create_record(
                        text=page_text,
                        file_path=file_path,
                        source_type="pdf",
                        page=page_number
                    )

                    records.append(record)

    except Exception as error:
        raise RuntimeError(
            f"PDF extraction failed: {error}"
        ) from error

    return records