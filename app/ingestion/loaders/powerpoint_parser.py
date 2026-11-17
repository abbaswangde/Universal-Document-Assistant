
from pathlib import Path
from pptx import Presentation


def parse_powerpoint(file_path):
    """
    Extract text from PowerPoint presentations.
    Supports slide titles, text boxes, tables and grouped shapes.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() != ".pptx":
        raise ValueError(
            f"Unsupported PowerPoint format: {file_path.suffix}"
        )

    presentation = Presentation(str(file_path))

    extracted_text = []

    def extract_shape_text(shape):
        """Extract text recursively from shapes and groups."""

        if shape.shape_type == 6:  # Group shape
            for child_shape in shape.shapes:
                extract_shape_text(child_shape)

        elif shape.has_table:
            for row in shape.table.rows:
                row_values = [
                    cell.text.strip()
                    for cell in row.cells
                    if cell.text.strip()
                ]

                if row_values:
                    extracted_text.append(" | ".join(row_values))

        elif shape.has_text_frame:
            text = shape.text.strip()

            if text:
                extracted_text.append(text)

    for slide_number, slide in enumerate(
        presentation.slides,
        start=1
    ):

        extracted_text.append(
            f"\nSlide {slide_number}"
        )

        for shape in slide.shapes:
            extract_shape_text(shape)

    return "\n".join(extracted_text)
