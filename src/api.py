import os
import shutil
import urllib.request
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.chain import build_qa_chain, query as rag_query
from src.ingest import run_ingestion
from src.config import DOCS_PATH, VECTOR_STORE_PATH


app = FastAPI(
    title="Enterprise RAG Copilot",
    description="Query your research papers using Llama 3 + FAISS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

qa_chain = None


@app.on_event("startup")
async def startup():
    global qa_chain
    try:
        qa_chain = build_qa_chain()
        print("QA chain loaded at startup!")
    except Exception as e:
        print(f"Chain not loaded at startup (run ingestion first): {e}")


# ── Request / Response Models ──────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    top_k:    int = 4

class QueryResponse(BaseModel):
    question: str
    answer:   str
    sources:  list

class IngestRequest(BaseModel):
    pdf_url:   str | None = None
    file_path: str | None = None


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "index_loaded": qa_chain is not None}


@app.get("/docs-list")
def list_documents():
    docs_path = Path(DOCS_PATH)
    if not docs_path.exists():
        return {"documents": [], "count": 0}
    files = [f.name for f in docs_path.glob("**/*.pdf")]
    return {"documents": files, "count": len(files)}


@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    global qa_chain
    if qa_chain is None:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base not ready. Add some papers first."
        )
    try:
        result = rag_query(req.question, chain=qa_chain)
        return QueryResponse(
            question=req.question,
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
def ingest_endpoint(req: IngestRequest):
    global qa_chain
    if req.pdf_url:
        os.makedirs(DOCS_PATH, exist_ok=True)
        fname     = req.pdf_url.split("/")[-1] + ".pdf"
        file_path = str(Path(DOCS_PATH) / fname)
        try:
            urllib.request.urlretrieve(req.pdf_url, file_path)
            print(f"Downloaded -> {file_path}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Download failed: {e}")
    elif req.file_path:
        file_path = req.file_path
    else:
        raise HTTPException(status_code=400, detail="Provide pdf_url or file_path")

    try:
        run_ingestion(file_path=file_path, incremental=True)
        # Force reload retriever cache
        import src.retriever as retriever_module
        retriever_module._vector_store = None
        qa_chain = build_qa_chain()
        return {"status": "success", "message": f"Ingested: {Path(file_path).name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest-all")
def ingest_all_endpoint():
    """Rebuild the entire index from all PDFs in data/docs/"""
    global qa_chain
    try:
        run_ingestion(file_path=None, incremental=False)
        # Force reload retriever cache
        import src.retriever as retriever_module
        retriever_module._vector_store = None
        qa_chain = build_qa_chain()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear-docs")
def clear_docs():
    """Delete all PDFs and the vector store — fresh start."""
    global qa_chain

    if Path(VECTOR_STORE_PATH).exists():
        shutil.rmtree(VECTOR_STORE_PATH)

    if Path(DOCS_PATH).exists():
        shutil.rmtree(DOCS_PATH)
    os.makedirs(DOCS_PATH, exist_ok=True)

    qa_chain = None
    return {"status": "success", "message": "All papers and index cleared"}
