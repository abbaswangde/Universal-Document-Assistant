
from docx import Document
from pathlib import Path


def parse_word(file_path):
    """
    Extract text from DOCX documents.
    Includes paragraphs and tables.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

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

            extracted_text.append(" | ".join(row_data))

    return "\n".join(extracted_text)
