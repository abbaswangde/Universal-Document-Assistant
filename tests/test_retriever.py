
from app.retrieval.retriever import search_documents


# Ask a question about the sample rental agreement
query = "What is the monthly rent?"

results = search_documents(
    query=query,
    collection_name="documents",
    top_k=3
)

print("\nSearch query:", query)
print("\nRetrieved chunks:", len(results))

for index, result in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print("Chunk ID:", result["id"])
    print("Page:", result["metadata"]["page"])
    print("Distance:", result["distance"])
    print("Text:")
    print(result["text"])
