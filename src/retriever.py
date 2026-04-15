from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import EMBEDDING_MODEL, VECTOR_STORE_PATH, TOP_K

_vector_store = None

def load_vector_store() -> FAISS:
    global _vector_store
    if _vector_store is None:
        print(f"Loading FAISS index from: {VECTOR_STORE_PATH}")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        _vector_store = FAISS.load_local(
            VECTOR_STORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print("Index loaded!")
    return _vector_store

def get_retriever(k: int = TOP_K):
    db = load_vector_store()
    return db.as_retriever(search_kwargs={"k": k})


def similarity_search(query: str, k: int = TOP_K) -> list:
    db      = load_vector_store()
    results = db.similarity_search(query, k=k)
    print(f"Found {len(results)} relevant chunks")
    return results
