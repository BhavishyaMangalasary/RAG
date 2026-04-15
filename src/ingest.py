import os
import argparse
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import (
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    VECTOR_STORE_PATH,
    DOCS_PATH,
)

def load_documents(file_path: str = None) -> list:
    if file_path:
        print(f"Loading single file: {file_path}")
        docs = PyPDFLoader(file_path).load()
    else:
        print(f"Loading all PDFs from: {DOCS_PATH}")
        docs = DirectoryLoader(
            DOCS_PATH,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
        ).load()
    print(f"Pages loaded: {len(docs)}")
    return docs

def split_documents(docs: list) -> list:
    print(f"Splitting into chunks — size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def get_embeddings():
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    print("(Downloads ~90MB the first time, then works offline forever)")
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def build_vector_store(chunks: list) -> FAISS:
    print(f"Embedding {len(chunks)} chunks and building FAISS index...")
    embeddings = get_embeddings()
    db = FAISS.from_documents(chunks, embeddings)
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    db.save_local(VECTOR_STORE_PATH)
    print(f"Index saved to: {VECTOR_STORE_PATH}")
    return db


def update_vector_store(chunks: list) -> FAISS:
    embeddings    = get_embeddings()
    index_file    = Path(VECTOR_STORE_PATH) / "index.faiss"

    if index_file.exists():
        print("Existing index found — adding new chunks...")
        db = FAISS.load_local(
            VECTOR_STORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        db.add_documents(chunks)
    else:
        print("No existing index — building fresh...")
        db = FAISS.from_documents(chunks, embeddings)

    db.save_local(VECTOR_STORE_PATH)
    print(f"Index saved to: {VECTOR_STORE_PATH}")
    return db

def run_ingestion(file_path: str = None, incremental: bool = False) -> None:
    docs = load_documents(file_path)
    if not docs:
        print("No documents found. Check your docs folder.")
        return
    chunks = split_documents(docs)
    if incremental:
        update_vector_store(chunks)
    else:
        build_vector_store(chunks)
    print("Ingestion complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",        type=str, default=None,
                        help="Path to a single PDF file")
    parser.add_argument("--incremental", action="store_true",
                        help="Add to existing index instead of rebuilding")
    args = parser.parse_args()
    run_ingestion(file_path=args.file, incremental=args.incremental)