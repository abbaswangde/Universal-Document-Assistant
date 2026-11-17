
import unittest
import tempfile
from pathlib import Path

from app.ingestion.loaders.legacy_converter import (
    convert_legacy_document
)


class TestLegacyConverter(unittest.TestCase):

    def test_missing_file(self):

        with self.assertRaises(FileNotFoundError):
            convert_legacy_document("missing.doc")

    def test_unsupported_format(self):

        with tempfile.NamedTemporaryFile(
            suffix=".pdf"
        ) as temp_file:

            with self.assertRaises(ValueError):
                convert_legacy_document(temp_file.name)


if __name__ == "__main__":
    unittest.main()
