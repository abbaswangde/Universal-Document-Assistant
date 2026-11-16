
from app.retrieval.retriever import search_documents
from app.generation.answer_generator import generate_answer


def start_chat():

    print("\n" + "=" * 45)
    print("       UNIVERSAL DOCUMENT ASSISTANT")
    print("=" * 45)

    print("\nDocument loaded: sample.pdf")
    print("Ask questions about your document.")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:

        try:
            # Get question from terminal
            query = input("You: ").strip()

            # Exit condition
            if query.lower() in ["exit", "quit"]:
                print("\nGoodbye! Thanks for using Universal Document Assistant.")
                break

            # Ignore empty input
            if not query:
                continue

            # Retrieve relevant chunks
            retrieved_chunks = search_documents(
                query=query,
                collection_name="documents",
                top_k=3
            )

            # Generate answer
            answer = generate_answer(
                query=query,
                retrieved_chunks=retrieved_chunks
            )

            print("\nAssistant:", answer)
            print("\n" + "-" * 45 + "\n")

        except KeyboardInterrupt:
            print("\n\nChat ended. Goodbye!")
            break

        except Exception as error:
            print(f"\nAn error occurred: {error}\n")


if __name__ == "__main__":
    start_chat()
