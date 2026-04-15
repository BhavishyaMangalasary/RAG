from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from src.config import GROQ_API_KEY, LLM_MODEL, TOP_K
from src.retriever import get_retriever


RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert research assistant helping users understand academic papers.
Use ONLY the context provided below to answer the question.
If the answer is not in the context, say: "I don't have enough information in the provided papers to answer this."

Context from papers:
{context}

Question: {question}

Answer (be clear and concise, mention which paper your answer comes from):"""
)


def build_qa_chain(k: int = TOP_K) -> RetrievalQA:
    llm = ChatGroq(
        model=LLM_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=0,
    )
    retriever = get_retriever(k=k)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": RAG_PROMPT},
    )
    print("QA chain ready!")
    return chain


def query(question: str, chain: RetrievalQA = None) -> dict:
    if chain is None:
        chain = build_qa_chain()
    result  = chain.invoke({"query": question})
    answer  = result["result"]
    sources = _format_sources(result.get("source_documents", []))
    return {"answer": answer, "sources": sources}


def _format_sources(docs: list) -> list:
    seen, sources = set(), []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        page   = doc.metadata.get("page", "?")
        key    = f"{source}::{page}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "file":    source.split("/")[-1],
                "page":    page,
                "excerpt": doc.page_content[:200].strip(),
            })
    return sources


if __name__ == "__main__":
    test_questions = [
        "What is the attention mechanism?",
        "How does RAG work?",
        "What problem does LoRA solve?",
    ]
    chain = build_qa_chain()
    for q in test_questions:
        print(f"\n{'='*60}\nQ: {q}")
        result = query(q, chain)
        print(f"A: {result['answer']}")
        print("\nSources:")
        for s in result["sources"]:
            print(f"  - {s['file']} (page {s['page']})")