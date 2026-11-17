
def split_into_chunks(records, chunk_size=1000, overlap=150):
    """
    Split document records into smaller text chunks.

    Supports records from all document loaders while preserving
    their metadata.

    Args:
        records: List of dictionaries containing text and metadata.
        chunk_size: Maximum target chunk length.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of chunk dictionaries.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

    chunks = []
    chunk_id = 0

    for record in records:

        text = record.get("text", "").strip()

        if not text:
            continue

        # Preserve metadata from the original document record.
        metadata = {
            key: value
            for key, value in record.items()
            if key != "text"
        }

        # Split text into paragraphs.
        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n")
            if paragraph.strip()
        ]

        current_chunk = ""

        def save_chunk(chunk_text):
            nonlocal chunk_id

            chunk_text = chunk_text.strip()

            if not chunk_text:
                return

            chunks.append({
                "chunk_id": chunk_id,
                **metadata,
                "text": chunk_text
            })

            chunk_id += 1

        for paragraph in paragraphs:

            # Handle paragraphs larger than chunk_size.
            if len(paragraph) > chunk_size:

                if current_chunk:
                    save_chunk(current_chunk)
                    current_chunk = ""

                start = 0
                step = chunk_size - overlap

                while start < len(paragraph):

                    piece = paragraph[start:start + chunk_size]

                    save_chunk(piece)

                    start += step

                continue

            # Add paragraph if it fits in the current chunk.
            if not current_chunk:
                current_chunk = paragraph

            elif len(current_chunk) + len(paragraph) + 1 <= chunk_size:
                current_chunk += "\n" + paragraph

            else:
                previous_chunk = current_chunk

                save_chunk(previous_chunk)

                # Retain overlap from the previous chunk.
                current_chunk = previous_chunk[-overlap:] + "\n" + paragraph if overlap else paragraph

        if current_chunk:
            save_chunk(current_chunk)

    return chunks
