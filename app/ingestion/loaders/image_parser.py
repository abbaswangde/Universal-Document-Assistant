
from pathlib import Path
from PIL import Image
import pytesseract

from app.ingestion.loaders.text_parser import create_record


SUPPORTED_FORMATS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
    ".bmp",
    ".webp",
    ".gif",
}


def parse_image(file_path):
    """
    Extract text from images using Tesseract OCR.

    Returns a list of standardized document records.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if file_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported image format: {file_path.suffix}"
        )

    try:
        with Image.open(file_path) as image:

            extracted_text = pytesseract.image_to_string(
                image
            ).strip()

            if not extracted_text:
                return []

            record = create_record(
                text=extracted_text,
                file_path=file_path,
                source_type="image",
                page=1
            )

            return [record]

    except Exception as error:
        raise RuntimeError(
            f"Image text extraction failed: {error}"
        ) from error
