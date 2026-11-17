
import unittest
import tempfile
from pathlib import Path

import openpyxl

from app.ingestion.loaders.excel_parser import parse_excel


class TestExcelParser(unittest.TestCase):

    def test_parse_xlsx(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "sample.xlsx"

            workbook = openpyxl.Workbook()

            sheet = workbook.active
            sheet.title = "Employees"

            sheet.append(["Name", "Age"])
            sheet.append(["Abbas", 25])
            sheet.append(["John", 30])

            workbook.save(file_path)

            result = parse_excel(file_path)

            self.assertIn("Sheet: Employees", result)
            self.assertIn("Name | Age", result)
            self.assertIn("Abbas | 25", result)
            self.assertIn("John | 30", result)

    def test_missing_file(self):

        with self.assertRaises(FileNotFoundError):
            parse_excel("nonexistent.xlsx")

    def test_unsupported_format(self):

        with tempfile.NamedTemporaryFile(
            suffix=".csv"
        ) as temp_file:

            with self.assertRaises(ValueError):
                parse_excel(temp_file.name)


if __name__ == "__main__":
    unittest.main()
