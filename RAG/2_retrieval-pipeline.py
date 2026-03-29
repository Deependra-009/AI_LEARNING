"""
Simple one-shot retrieval + answer generation pipeline.
"""

from typing import Callable

from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from RAG.config import SETTINGS, create_chat_model, create_vector_store

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant.

Answer the question using ONLY the provided context.
- First give a direct answer.
- Then a short explanation.
- If not found, say "I don't know".

Context:
{context}

Question:
{question}
""")

def format_docs(docs) -> str:
    """Convert list of docs to a single string for the prompt."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_chain(k: int = 3) -> Runnable:
    """
    Build a retrieval + generation chain that can be reused.

    Returns a Runnable that accepts a user question (str) and returns an answer (str).
    """
    db = create_vector_store()
    retriever = db.as_retriever(search_kwargs={"k": k})
    llm = create_chat_model()

    chain: Runnable = (
        {
            "context": retriever | format_docs,
            "question": lambda x: x,
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def answer_question(question: str, chain: Runnable | None = None) -> str:
    """Convenience wrapper for answering a single question."""
    if chain is None:
        chain = build_chain()
    return chain.invoke(question)


def main() -> None:
    """Run a simple demo query against the retrieval pipeline."""
    question = "When was Google founded?"
    chain = build_chain()
    response = chain.invoke(question)

    print("\nUser Query:", question)
    print("\nAnswer:\n", response)


if __name__ == "__main__":
    main()