
def split_into_chunks(pages, chunk_size=1000, overlap=150):
    """
    Split extracted PDF text into smaller chunks.

    Each chunk retains its original page number.
    """

    chunks = []
    chunk_id = 0

    for page in pages:
        page_number = page["page"]
        text = page["text"].strip()

        if not text:
            continue

        # Split text into paragraphs
        paragraphs = [
            p.strip()
            for p in text.split("\n")
            if p.strip()
        ]

        current_chunk = ""

        for paragraph in paragraphs:

            # Handle paragraphs larger than the chunk size
            if len(paragraph) > chunk_size:
                if current_chunk:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "page": page_number,
                        "text": current_chunk
                    })
                    chunk_id += 1
                    current_chunk = ""

                start = 0

                while start < len(paragraph):
                    piece = paragraph[start:start + chunk_size]

                    chunks.append({
                        "chunk_id": chunk_id,
                        "page": page_number,
                        "text": piece
                    })
                    chunk_id += 1
                    start += chunk_size - overlap

                continue

            # Add paragraph to current chunk if it fits
            if len(current_chunk) + len(paragraph) + 1 <= chunk_size:
                current_chunk += "\n" + paragraph if current_chunk else paragraph

            else:
                # Save the current chunk
                if current_chunk:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "page": page_number,
                        "text": current_chunk
                    })
                    chunk_id += 1

                # Start the next chunk with a small overlap
                current_chunk = current_chunk[-overlap:] + "\n" + paragraph

        # Save remaining text from the page
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "page": page_number,
                "text": current_chunk.strip()
            })
            chunk_id += 1

    return chunks
