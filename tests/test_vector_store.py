
import unittest
import tempfile

from app.ingestion.vector_store import store_embeddings, get_chroma_client


class TestVectorStore(unittest.TestCase):

    def test_store_embeddings(self):

        chunks = [
            {
                "chunk_id": 0,
                "text": "Universal Document Assistant",
                "page": 1,
                "source": "sample.pdf",
                "source_type": "pdf"
            }
        ]

        embeddings = [[0.1, 0.2, 0.3]]

        with tempfile.TemporaryDirectory() as temp_dir:

            total = store_embeddings(
                chunks=chunks,
                embeddings=embeddings,
                collection_name="test_documents",
                document_id="test_sample",
                persist_directory=temp_dir
            )

            self.assertEqual(total, 1)

            client = get_chroma_client(temp_dir)
            collection = client.get_collection("test_documents")

            result = collection.get(
                ids=["test_sample_0"],
                include=["documents", "metadatas"]
            )

            self.assertEqual(
                result["documents"][0],
                "Universal Document Assistant"
            )

            metadata = result["metadatas"][0]

            self.assertEqual(metadata["source"], "sample.pdf")
            self.assertEqual(metadata["source_type"], "pdf")
            self.assertEqual(metadata["page"], 1)
            self.assertEqual(metadata["document_id"], "test_sample")

    def test_metadata_preservation(self):

        chunks = [
            {
                "chunk_id": 0,
                "text": "January sales data",
                "source": "sales.xlsx",
                "source_type": "excel",
                "sheet": "January"
            }
        ]

        embeddings = [[0.1, 0.2, 0.3]]

        with tempfile.TemporaryDirectory() as temp_dir:

            store_embeddings(
                chunks,
                embeddings,
                collection_name="test_excel",
                document_id="sales",
                persist_directory=temp_dir
            )

            client = get_chroma_client(temp_dir)
            collection = client.get_collection("test_excel")

            result = collection.get(
                ids=["sales_0"],
                include=["metadatas"]
            )

            metadata = result["metadatas"][0]

            self.assertEqual(metadata["sheet"], "January")
            self.assertEqual(metadata["source_type"], "excel")

    def test_mismatched_embeddings(self):

        chunks = [
            {
                "chunk_id": 0,
                "text": "Sample text"
            }
        ]

        embeddings = []

        with self.assertRaises(ValueError):
            store_embeddings(chunks, embeddings)


if __name__ == "__main__":
    unittest.main()
