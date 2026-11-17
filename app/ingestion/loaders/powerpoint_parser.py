
from pathlib import Path
from pptx import Presentation

from app.ingestion.loaders.text_parser import create_record


def parse_powerpoint(file_path):
    """
    Extract text from PowerPoint presentations.

    Supports slide titles, text boxes, tables and grouped shapes.
    Returns one standardized record per slide.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if file_path.suffix.lower() != ".pptx":
        raise ValueError(
            f"Unsupported PowerPoint format: {file_path.suffix}"
        )

    try:
        presentation = Presentation(str(file_path))
        records = []

        def extract_shape_text(shape, extracted_text):
            """Extract text recursively from shapes and groups."""

            # Group shape
            if shape.shape_type == 6:
                for child_shape in shape.shapes:
                    extract_shape_text(child_shape, extracted_text)

            # Table
            elif shape.has_table:
                for row in shape.table.rows:
                    row_values = [
                        cell.text.strip()
                        for cell in row.cells
                        if cell.text.strip()
                    ]

                    if row_values:
                        extracted_text.append(
                            " | ".join(row_values)
                        )

            # Text box or title
            elif shape.has_text_frame:
                text = shape.text.strip()

                if text:
                    extracted_text.append(text)

        for slide_number, slide in enumerate(
            presentation.slides,
            start=1
        ):

            extracted_text = []

            for shape in slide.shapes:
                extract_shape_text(shape, extracted_text)

            full_text = "\n".join(extracted_text).strip()

            if not full_text:
                continue

            record = create_record(
                text=full_text,
                file_path=file_path,
                source_type="pptx",
                page=slide_number
            )

            record["slide"] = slide_number

            records.append(record)

        return records

    except Exception as error:
        raise RuntimeError(
            f"PowerPoint extraction failed: {error}"
        ) from error
