
from pathlib import Path
from docx import Document

from app.ingestion.loaders.text_parser import create_record


def parse_word(file_path):
    """
    Extract text from DOCX documents.
    Includes paragraphs and tables.

    Returns a list of standardized records.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    try:
        document = Document(file_path)

        extracted_text = []

        # Extract paragraphs
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                extracted_text.append(text)

        # Extract tables
        for table in document.tables:
            for row in table.rows:
                row_data = [
                    cell.text.strip()
                    for cell in row.cells
                ]

                if any(row_data):
                    extracted_text.append(
                        " | ".join(row_data)
                    )

        full_text = "\n".join(extracted_text).strip()

        if not full_text:
            return []

        return [
            create_record(
                text=full_text,
                file_path=file_path,
                source_type="docx",
                page=1
            )
        ]

    except Exception as error:
        raise RuntimeError(
            f"Word document extraction failed: {error}"
        ) from error
