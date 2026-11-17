
from pathlib import Path
import pymupdf


def parse_pdf(file_path):
    """
    Extract text from PDF documents using PyMuPDF.
    Preserves page numbers and handles multi-page PDFs.
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

    extracted_text = []

    try:
        with pymupdf.open(file_path) as document:

            for page_number, page in enumerate(
                document,
                start=1
            ):

                page_text = page.get_text("text").strip()

                if page_text:
                    extracted_text.append(
                        f"\nPage {page_number}\n{page_text}"
                    )

    except Exception as error:
        raise RuntimeError(
            f"PDF extraction failed: {error}"
        ) from error

    return "\n".join(extracted_text).strip()
