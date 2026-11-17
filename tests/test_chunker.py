
import unittest

from app.ingestion.chunker import split_into_chunks


class TestChunker(unittest.TestCase):

    def test_basic_chunking(self):

        records = [{
            "text": "This is a test document.\nIt contains multiple paragraphs.",
            "page": 1
        }]

        chunks = split_into_chunks(records, chunk_size=100,overlap=20)

        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0]["page"], 1)

    def test_metadata_preservation(self):

        records = [{
            "text": "Excel worksheet content",
            "source": "sales.xlsx",
            "source_type": "excel",
            "sheet": "January",
            "page": 1
        }]

        chunks = split_into_chunks(records)

        self.assertEqual(chunks[0]["source"], "sales.xlsx")
        self.assertEqual(chunks[0]["source_type"], "excel")
        self.assertEqual(chunks[0]["sheet"], "January")

    def test_large_paragraph(self):

        records = [{
            "text": "A" * 2500,
            "page": 1
        }]

        chunks = split_into_chunks(
            records,
            chunk_size=1000,
            overlap=150
        )

        self.assertGreater(len(chunks), 1)

        for chunk in chunks:
            self.assertLessEqual(len(chunk["text"]), 1000)

    def test_empty_records(self):

        chunks = split_into_chunks([
            {"text": "", "page": 1}
        ])

        self.assertEqual(chunks, [])

    def test_invalid_chunk_size(self):

        with self.assertRaises(ValueError):
            split_into_chunks([], chunk_size=0)

    def test_invalid_overlap(self):

        with self.assertRaises(ValueError):
            split_into_chunks([], chunk_size=100, overlap=100)


if __name__ == "__main__":
    unittest.main()
