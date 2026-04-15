import os
from dotenv import load_dotenv

load_dotenv()

# Groq (free LLM)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL    = os.getenv("LLM_MODEL", "llama3-8b-8192")

# HuggingFace Embeddings (free, runs on your laptop)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Chunking
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# Paths
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store")
DOCS_PATH         = os.getenv("DOCS_PATH", "./data/docs")

# Retrieval
TOP_K = int(os.getenv("TOP_K", 4))