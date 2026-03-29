"""
History-aware RAG chat:
- Rewrites the user question using chat history.
- Retrieves relevant documents from Chroma.
- Generates a final answer using the retrieved context.
"""

from typing import List, Union

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from RAG.config import create_chat_model, create_vector_store


chat_model = create_chat_model()
vector_store = create_vector_store()

chat_history: List[Union[HumanMessage, AIMessage]] = []


def rewrite_question_with_history(question: str) -> str:
    """Rewrite the user question as a standalone, search-friendly query."""
    if not chat_history:
        return question

    messages = [
        SystemMessage(
            content="Given the chat history, rewrite the new question to be standalone and searchable."
        ),
        *chat_history,
        HumanMessage(content=f"New Question: {question}"),
    ]
    result = chat_model.invoke(messages)
    return result.content.strip()


def retrieve_documents(search_query: str, k: int = 3) -> List[Document]:
    """Retrieve documents relevant to the search query."""
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs: List[Document] = retriever.invoke(search_query)
    return docs


def format_docs(docs: List[Document]) -> str:
    """Format documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def generate_answer(user_question: str, docs: List[Document]) -> str:
    """Generate a final answer using retrieved docs as context."""
    context = format_docs(docs)
    messages = [
        SystemMessage(
            content=(
                "You are a helpful assistant.\n"
                "Answer the question using ONLY the provided context.\n"
                "- First give a direct answer.\n"
                "- Then a short explanation.\n"
                "- If not found, say \"I don't know\"."
            )
        ),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion:\n{user_question}"),
    ]
    result = chat_model.invoke(messages)
    return result.content.strip()


def ask_question(user_question: str) -> None:
    """Handle a single user question with history-aware retrieval and answer generation."""
    print(f"\n-- You asked: {user_question}")

    search_question = rewrite_question_with_history(user_question)
    if search_question != user_question:
        print(f"Searching for (rewritten): {search_question}")

    docs = retrieve_documents(search_question)

    # Show retrieved docs (debugging / transparency)
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Document {i} ---")
        print(doc.page_content[:300])
        print("Metadata:", doc.metadata)

    # Generate final answer based on retrieved context
    answer = generate_answer(user_question, docs)
    print("\n--- Answer ---")
    print(answer)

    # Update chat history with the latest turn
    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=answer))


def start_chat() -> None:
    """Simple CLI loop for interactive questioning."""
    print("Ask me questions! Type 'quit' to exit.")

    while True:
        question = input("\nYour question: ")
        if question.lower().strip() == "quit":
            print("Goodbye.")
            break

        ask_question(question)


if __name__ == "__main__":
    start_chat()
