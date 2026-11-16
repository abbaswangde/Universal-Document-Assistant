
import pymupdf


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A list containing text and page numbers.
    """

    extracted_pages = []

    # Open the PDF document
    document = pymupdf.open(pdf_path)

    # Read each page
    for page_number, page in enumerate(document, start=1):

        # Extract text from the current page
        text = page.get_text("text")

        # Store page number and extracted text
        extracted_pages.append({
            "page": page_number,
            "text": text
        })

    # Close the PDF
    document.close()

    return extracted_pages
