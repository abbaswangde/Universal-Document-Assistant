
import csv
import json
from pathlib import Path

from bs4 import BeautifulSoup


def create_record(text, file_path, source_type, page=1):
    """Create a standardized text record for the ingestion pipeline."""
    return {
        "text": text.strip(),
        "source": Path(file_path).name,
        "source_type": source_type,
        "page": page,
        "section": None,
        "sheet": None,
        "slide": None,
    }


def parse_txt(file_path):
    """Extract text from TXT and Markdown files."""
    file_path = Path(file_path)

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]

    for encoding in encodings:
        try:
            text = file_path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Could not decode file: {file_path.name}")

    if not text.strip():
        return []

    return [
        create_record(text, file_path, "txt")
    ]


def parse_csv(file_path, rows_per_record=20):
    """Extract CSV data in groups of rows, retaining column headers."""
    file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        sample = file.read(4096)
        file.seek(0)

        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel

        reader = csv.reader(file, dialect)
        rows = list(reader)

    if not rows:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    records = []

    for index in range(0, len(data_rows), rows_per_record):
        batch = data_rows[index:index + rows_per_record]

        lines = [
            "Columns: " + " | ".join(headers)
        ]

        for row in batch:
            lines.append(
                " | ".join(
                    f"{headers[i]}: {value}"
                    for i, value in enumerate(row)
                    if i < len(headers)
                )
            )

        text = "\n".join(lines)

        records.append(
            create_record(
                text,
                file_path,
                "csv",
                page=len(records) + 1
            )
        )

    return records


def parse_json(file_path):
    """Extract readable text from JSON files."""
    file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    text = json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    )

    if not text.strip():
        return []

    return [
        create_record(text, file_path, "json")
    ]


def parse_html(file_path):
    """Extract readable text from HTML files."""
    file_path = Path(file_path)

    html = file_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    # Remove content that usually isn't useful for document search.
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)

    if not text.strip():
        return []

    return [
        create_record(text, file_path, "html")
    ]


def load_text_document(file_path):
    """Choose the correct parser based on the file extension."""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    parsers = {
        ".txt": parse_txt,
        ".md": parse_txt,
        ".csv": parse_csv,
        ".json": parse_json,
        ".html": parse_html,
        ".htm": parse_html,
    }

    parser = parsers.get(extension)

    if parser is None:
        raise ValueError(
            f"Unsupported text document format: {extension}"
        )

    return parser(file_path)
