import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ----------------------------
# DB Setup
# ----------------------------
persist_directory = "db/chroma_db"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model,
)

retriever = db.as_retriever(search_kwargs={"k": 3})

# ----------------------------
# LLM
# ----------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ----------------------------
# Prompt
# ----------------------------
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

# ----------------------------
# Helper: format docs
# ----------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# ----------------------------
# LCEL Chain
# ----------------------------
chain = (
    {
        "context": retriever | format_docs,
        "question": lambda x: x
    }
    | prompt
    | llm
    | StrOutputParser()
)

# ----------------------------
# Query
# ----------------------------
query = "When was Google founded?"

response = chain.invoke(query)

print("\nUser Query:", query)
print("\nAnswer:\n", response)