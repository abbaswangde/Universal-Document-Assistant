
import tempfile
import unittest
from pathlib import Path

from app.ingestion.loaders.text_parser import load_text_document


class TestTextParser(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_txt(self):
        path = self.test_dir / "sample.txt"
        path.write_text("This is a sample text document.", encoding="utf-8")

        records = load_text_document(path)

        self.assertEqual(len(records), 1)
        self.assertIn("sample text document", records[0]["text"])
        self.assertEqual(records[0]["source_type"], "txt")

    def test_csv(self):
        path = self.test_dir / "sample.csv"
        path.write_text(
            "Name,Age\nAbbas,25\nJohn,30\n",
            encoding="utf-8"
        )

        records = load_text_document(path)

        self.assertEqual(len(records), 1)
        self.assertIn("Name: Abbas", records[0]["text"])
        self.assertEqual(records[0]["source_type"], "csv")

    def test_json(self):
        path = self.test_dir / "sample.json"
        path.write_text(
            '{"name": "Abbas", "role": "Developer"}',
            encoding="utf-8"
        )

        records = load_text_document(path)

        self.assertEqual(len(records), 1)
        self.assertIn("Developer", records[0]["text"])
        self.assertEqual(records[0]["source_type"], "json")

    def test_html(self):
        path = self.test_dir / "sample.html"
        path.write_text(
            """
            <html>
                <head><title>Test</title></head>
                <body>
                    <h1>Document Assistant</h1>
                    <p>HTML extraction is working.</p>
                    <script>ignore this</script>
                </body>
            </html>
            """,
            encoding="utf-8"
        )

        records = load_text_document(path)

        self.assertEqual(len(records), 1)
        self.assertIn("Document Assistant", records[0]["text"])
        self.assertNotIn("ignore this", records[0]["text"])
        self.assertEqual(records[0]["source_type"], "html")


if __name__ == "__main__":
    unittest.main()
