
from pathlib import Path
import tempfile

from app.ingestion.loaders.text_parser import load_text_document
from app.ingestion.loaders.word_parser import parse_word
from app.ingestion.loaders.excel_parser import parse_excel
from app.ingestion.loaders.powerpoint_parser import parse_powerpoint
from app.ingestion.loaders.image_parser import parse_image
from app.ingestion.loaders.pdf_parser import parse_pdf
from app.ingestion.loaders.legacy_converter import convert_legacy_document


# Supported modern document formats
PARSER_MAP = {
    ".txt": load_text_document,
    ".md": load_text_document,
    ".csv": load_text_document,
    ".json": load_text_document,
    ".html": load_text_document,
    ".htm": load_text_document,
    ".docx": parse_word,
    ".xlsx": parse_excel,
    ".pptx": parse_powerpoint,
    ".pdf": parse_pdf,
    ".png": parse_image,
    ".jpg": parse_image,
    ".jpeg": parse_image,
    ".tiff": parse_image,
    ".tif": parse_image,
    ".bmp": parse_image,
    ".webp": parse_image,
     ".gif": parse_image,
}

# Older formats that need conversion first
LEGACY_FORMATS = {
    ".doc",
    ".xls",
    ".ppt",
}


def load_document(file_path):
    """
    Automatically detect and extract content from supported documents.

    Returns standardized document information containing:
    filename, file_type, content, and character_count.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = file_path.suffix.lower()

    try:
        if extension in PARSER_MAP:
            records = PARSER_MAP[extension](file_path)

        elif extension in LEGACY_FORMATS:
            converted = convert_legacy_document(file_path)

            with tempfile.TemporaryDirectory() as temp_dir:
                converted_path = Path(temp_dir) / converted["filename"]
                converted_path.write_bytes(converted["content"])

                converted_extension = converted_path.suffix.lower()

                if converted_extension not in PARSER_MAP:
                    raise ValueError(
                        f"Unsupported converted format: {converted_extension}"
                    )

                records = PARSER_MAP[converted_extension](converted_path)

        else:
            raise ValueError(
                f"Unsupported document format: {extension}"
            )

        # All parsers should return a list of standardized records.
        if not isinstance(records, list):
            raise TypeError(
                "Document parser must return a list of records."
            )

        character_count = sum(
            len(record.get("text", ""))
            for record in records
            if isinstance(record, dict)
        )

        return {
            "filename": file_path.name,
            "file_type": extension,
            "content": records,
            "character_count": character_count,
        }

    except Exception as error:
        raise RuntimeError(
            f"Document loading failed for {file_path.name}: {error}"
        ) from error
