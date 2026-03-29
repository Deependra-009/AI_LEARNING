"""
Ingestion pipeline: loads raw documents, chunks them, and writes to Chroma.
"""

import os
from typing import List

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter

from RAG.config import (
    SETTINGS,
    create_embedding_model,
    ensure_directories,
)


def load_documents(docs_path: str = SETTINGS.docs_path) -> List[Document]:
    """Load documents from a directory."""
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist: {docs_path}")

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader
    )
    documents: List[Document] = loader.load()
    print(f"Loaded {len(documents)} documents from {docs_path}")
    return documents


def split_documents(
    documents: List[Document],
    chunk_size: int = SETTINGS.chunk_size,
    chunk_overlap: int = SETTINGS.chunk_overlap,
) -> List[Document]:
    """Split documents into smaller chunks."""
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks: List[Document] = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def create_vector_store(
    chunks: List[Document],
    persist_directory: str = SETTINGS.persist_directory,
):
    """Create or update the Chroma vector store from document chunks."""
    embedding_model = create_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"Vector store created/updated at: {persist_directory}")
    return vector_store


def main():
    """Entry point for the ingestion pipeline."""
    print("=== RAG Ingestion Pipeline ===")
    ensure_directories()
    documents = load_documents()

    chunks = split_documents(documents)

    vector_store = create_vector_store(chunks)

    # 4️⃣ Example retrieval for debugging
    # retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    # query = "When was Google founded?"
    # retrieved_docs = retriever.get_relevant_documents(query)
    #
    # print(f"\nQuery: {query}")
    # for i, doc in enumerate(retrieved_docs, 1):
    #     print(f"\n--- Document {i} ---")
    #     print(doc.page_content[:500])  # print first 500 chars
    #     print("Metadata:", doc.metadata)
    
    # print("\n=== Pipeline finished successfully ===")


if __name__ == "__main__":
    main()