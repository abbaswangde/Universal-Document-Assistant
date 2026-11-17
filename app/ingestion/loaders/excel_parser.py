
from pathlib import Path

import openpyxl
import xlrd

from app.ingestion.loaders.text_parser import create_record


def parse_excel(file_path):
    """
    Extract text from XLSX and XLS spreadsheets.

    Returns one standardized record per worksheet.
    Preserves worksheet names in metadata.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    records = []

    if extension == ".xlsx":

        workbook = openpyxl.load_workbook(
            file_path,
            data_only=True,
            read_only=True
        )

        try:
            for sheet_index, sheet in enumerate(workbook.worksheets):

                extracted_rows = []

                for row in sheet.iter_rows(values_only=True):

                    row_values = [
                        str(value).strip()
                        for value in row
                        if value is not None
                    ]

                    if row_values:
                        extracted_rows.append(
                            " | ".join(row_values)
                        )

                text = "\n".join(extracted_rows).strip()

                if text:
                    record = create_record(
                        text=text,
                        file_path=file_path,
                        source_type="xlsx",
                        page=sheet_index + 1
                    )

                    record["sheet"] = sheet.title
                    records.append(record)

        finally:
            workbook.close()

    elif extension == ".xls":

        workbook = xlrd.open_workbook(str(file_path))

        try:
            for sheet_index, sheet in enumerate(workbook.sheets()):

                extracted_rows = []

                for row_index in range(sheet.nrows):

                    row_values = [
                        str(value).strip()
                        for value in sheet.row_values(row_index)
                        if value != ""
                    ]

                    if row_values:
                        extracted_rows.append(
                            " | ".join(row_values)
                        )

                text = "\n".join(extracted_rows).strip()

                if text:
                    record = create_record(
                        text=text,
                        file_path=file_path,
                        source_type="xls",
                        page=sheet_index + 1
                    )

                    record["sheet"] = sheet.name
                    records.append(record)

        finally:
            workbook.release_resources()

    else:
        raise ValueError(
            f"Unsupported Excel format: {extension}"
        )

    return records
