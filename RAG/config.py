"""
Shared configuration and factory helpers for the RAG pipelines.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()


@dataclass(frozen=True)
class RAGSettings:
    """Central configuration for all RAG scripts."""

    docs_path: str = "docs"
    persist_directory: str = "db/chroma_db"
    chunk_size: int = 1000
    chunk_overlap: int = 100
    embedding_model_name: str = "text-embedding-3-small"
    llm_model_name: str = "gpt-4o-mini"
    llm_temperature: float = 0.0


SETTINGS = RAGSettings()


def ensure_directories() -> None:
    """Create required directories if they don't exist."""
    os.makedirs(SETTINGS.docs_path, exist_ok=True)
    os.makedirs(SETTINGS.persist_directory, exist_ok=True)


def create_embedding_model() -> OpenAIEmbeddings:
    """Factory for the shared embedding model."""
    return OpenAIEmbeddings(model=SETTINGS.embedding_model_name)


def create_vector_store() -> Chroma:
    """
    Factory for the shared Chroma vector store.

    Assumes the ingestion pipeline has already populated the DB.
    """
    return Chroma(
        persist_directory=SETTINGS.persist_directory,
        embedding_function=create_embedding_model(),
    )


def create_chat_model() -> ChatOpenAI:
    """Factory for the shared chat model."""
    return ChatOpenAI(
        model=SETTINGS.llm_model_name,
        temperature=SETTINGS.llm_temperature,
    )

