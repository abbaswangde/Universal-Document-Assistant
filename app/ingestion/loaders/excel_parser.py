
from pathlib import Path
import openpyxl
import xlrd


def parse_excel(file_path):
    """
    Extract text from XLSX and XLS spreadsheets.
    Supports multiple worksheets.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = file_path.suffix.lower()

    extracted_text = []

    if extension == ".xlsx":

        workbook = openpyxl.load_workbook(
            file_path,
            data_only=True,
            read_only=True
        )

        for sheet in workbook.worksheets:

            extracted_text.append(
                f"\nSheet: {sheet.title}"
            )

            for row in sheet.iter_rows(values_only=True):

                row_values = [
                    str(value).strip()
                    for value in row
                    if value is not None
                ]

                if row_values:
                    extracted_text.append(
                        " | ".join(row_values)
                    )

        workbook.close()

    elif extension == ".xls":

        workbook = xlrd.open_workbook(str(file_path))

        for sheet in workbook.sheets():

            extracted_text.append(
                f"\nSheet: {sheet.name}"
            )

            for row_index in range(sheet.nrows):

                row_values = [
                    str(value).strip()
                    for value in sheet.row_values(row_index)
                    if value != ""
                ]

                if row_values:
                    extracted_text.append(
                        " | ".join(row_values)
                    )

    else:
        raise ValueError(
            f"Unsupported Excel format: {extension}"
        )

    return "\n".join(extracted_text)
