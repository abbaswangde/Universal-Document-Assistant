
import unittest
import tempfile
from pathlib import Path

from app.ingestion.loaders.document_loader import load_document


class TestDocumentLoader(unittest.TestCase):

    def test_load_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "sample.txt"

            file_path.write_text(
                "Universal Document Assistant Test",
                encoding="utf-8"
            )

            result = load_document(file_path)

            self.assertEqual(result["filename"], "sample.txt")
            self.assertEqual(result["file_type"], ".txt")

            self.assertIsInstance(result["content"], list)
            self.assertGreater(len(result["content"]), 0)

            self.assertIn(
                "Universal Document Assistant Test",
                result["content"][0]["text"]
            )

            self.assertGreater(result["character_count"], 0)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_document("missing_file.pdf")

    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz") as temp_file:
            with self.assertRaises(RuntimeError):
                load_document(temp_file.name)


if __name__ == "__main__":
    unittest.main()
