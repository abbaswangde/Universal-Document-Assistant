
import unittest
import tempfile
import numpy as np

from unittest.mock import patch

from app.ingestion.vector_store import store_embeddings
from app.retrieval.retriever import search_documents


class FakeEmbeddingModel:

    def encode(self, *args, **kwargs):
        return np.array([1.0, 0.0, 0.0])


class TestRetriever(unittest.TestCase):

    def test_search_documents(self):

        chunks = [
            {
                "chunk_id": 0,
                "text": "The monthly rent is 1500 dollars.",
                "source": "rental.pdf",
                "source_type": "pdf",
                "page": 2
            },
            {
                "chunk_id": 1,
                "text": "The security deposit is 500 dollars.",
                "source": "rental.pdf",
                "source_type": "pdf",
                "page": 3
            }
        ]

        embeddings = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ]

        with tempfile.TemporaryDirectory() as temp_dir:

            store_embeddings(
                chunks=chunks,
                embeddings=embeddings,
                collection_name="test_retriever",
                document_id="rental",
                persist_directory=temp_dir
            )

            with patch(
                "app.retrieval.retriever.load_embedding_model",
                return_value=FakeEmbeddingModel()
            ):

                results = search_documents(
                    query="What is the monthly rent?",
                    collection_name="test_retriever",
                    top_k=2,
                    document_id="rental",
                    persist_directory=temp_dir
                )

            self.assertEqual(len(results), 2)

            self.assertIn(
                "monthly rent",
                results[0]["text"]
            )

            metadata = results[0]["metadata"]

            self.assertEqual(metadata["source"], "rental.pdf")
            self.assertEqual(metadata["source_type"], "pdf")
            self.assertEqual(metadata["page"], 2)

    def test_empty_query(self):

        with self.assertRaises(ValueError):
            search_documents("")

    def test_invalid_top_k(self):

        with self.assertRaises(ValueError):
            search_documents("monthly rent", top_k=0)


if __name__ == "__main__":
    unittest.main()
