
from app.retrieval.retriever import search_documents
from app.generation.answer_generator import generate_answer


# Step 1: Ask a question
query = "What is the tenant's phone number?"

print("\nQuestion:", query)

# Step 2: Retrieve relevant document chunks
retrieved_chunks = search_documents(
    query=query,
    collection_name="documents",
    top_k=3
)

print("\nRetrieved chunks:", len(retrieved_chunks))

# Step 3: Generate an answer using Ollama
answer = generate_answer(
    query=query,
    retrieved_chunks=retrieved_chunks
)

# Step 4: Display the answer
print("\n========== AI ANSWER ==========")
print(answer)
print("===============================")
