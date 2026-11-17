
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
            workbook.close()

            result = parse_excel(file_path)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)

            record = result[0]

            self.assertIn("Name | Age", record["text"])
            self.assertIn("Abbas | 25", record["text"])
            self.assertIn("John | 30", record["text"])

            self.assertEqual(record["source"], "sample.xlsx")
            self.assertEqual(record["source_type"], "xlsx")
            self.assertEqual(record["sheet"], "Employees")
            self.assertEqual(record["page"], 1)

    def test_multiple_worksheets(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "multiple.xlsx"

            workbook = openpyxl.Workbook()

            sheet1 = workbook.active
            sheet1.title = "Employees"
            sheet1.append(["Name", "Abbas"])

            sheet2 = workbook.create_sheet("Departments")
            sheet2.append(["Department", "IT"])

            workbook.save(file_path)
            workbook.close()

            result = parse_excel(file_path)

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["sheet"], "Employees")
            self.assertEqual(result[1]["sheet"], "Departments")

    def test_empty_worksheet(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "empty.xlsx"

            workbook = openpyxl.Workbook()
            workbook.save(file_path)
            workbook.close()

            result = parse_excel(file_path)

            self.assertEqual(result, [])

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
