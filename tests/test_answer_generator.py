
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from app.generation.answer_generator import (
    generate_answer,
    format_source_location
)


class TestAnswerGenerator(unittest.TestCase):

    def test_empty_retrieved_chunks(self):

        answer = generate_answer(
            "What is the rent?",
            []
        )

        self.assertIn("couldn't find", answer)

    def test_pdf_source_location(self):

        metadata = {
            "source": "rental.pdf",
            "page": 2
        }

        result = format_source_location(metadata)

        self.assertEqual(
            result,
            "rental.pdf | Page 2"
        )

    def test_excel_source_location(self):

        metadata = {
            "source": "sales.xlsx",
            "sheet": "January"
        }

        result = format_source_location(metadata)

        self.assertEqual(
            result,
            "sales.xlsx | Sheet: January"
        )

    def test_powerpoint_source_location(self):

        metadata = {
            "source": "presentation.pptx",
            "slide": 4
        }

        result = format_source_location(metadata)

        self.assertEqual(
            result,
            "presentation.pptx | Slide 4"
        )

    @patch("app.generation.answer_generator.ollama.chat")
    def test_generate_answer(self, mock_chat):

        mock_chat.return_value = SimpleNamespace(
            message=SimpleNamespace(
                content="The monthly rent is 1500 dollars."
            )
        )

        chunks = [
            {
                "text": "The monthly rent is 1500 dollars.",
                "metadata": {
                    "source": "rental.pdf",
                    "page": 2
                }
            }
        ]

        answer = generate_answer(
            "What is the monthly rent?",
            chunks
        )

        self.assertEqual(
            answer,
            "The monthly rent is 1500 dollars."
        )

        prompt = mock_chat.call_args.kwargs["messages"][0]["content"]

        self.assertIn("rental.pdf", prompt)
        self.assertIn("Page 2", prompt)


if __name__ == "__main__":
    unittest.main()
