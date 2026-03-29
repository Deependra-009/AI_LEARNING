import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# ----------------------------
# Configurations
# ----------------------------
DOCS_PATH = "docs"
PERSIST_DIRECTORY = "db/chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100  # some overlap helps context in retrieval
EMBEDDING_MODEL_NAME = "text-embedding-3-small"


# ----------------------------
# Load documents
# ----------------------------
def load_documents(docs_path=DOCS_PATH):
    """Load documents from a directory"""
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist: {docs_path}")

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {docs_path}")
    return documents


# ----------------------------
# Split documents into chunks
# ----------------------------
def split_documents(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Split documents into smaller chunks"""
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


# ----------------------------
# Create or load vector store
# ----------------------------
def create_vector_store(chunks, persist_directory=PERSIST_DIRECTORY):
    """Create Chroma vector store from document chunks"""
    embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

    # Create or load existing vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"Vector store created/updated at: {persist_directory}")
    return vector_store


# ----------------------------
# Format documents for LCEL/Prompt
# ----------------------------
def format_docs(docs):
    """Convert list of docs to a single string for prompt"""
    return "\n\n".join([doc.page_content for doc in docs])


# ----------------------------
# Main pipeline
# ----------------------------
def main():
    print("=== RAG Ingestion Pipeline ===")

    # 1️⃣ Load documents
    documents = load_documents()

    # 2️⃣ Chunk documents
    chunks = split_documents(documents)

    # 3️⃣ Create vector store
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
    #
    # print("\n=== Pipeline finished successfully ===")


if __name__ == "__main__":
    main()