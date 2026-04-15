#🔍 Research Paper Copilot

> Ask questions across research papers and get grounded answers with citations — powered by Llama 3, FAISS, and LangChain. 100% free to run.

---

## 📖 Description

Research Paper Copilot is an enterprise-grade AI assistant that lets you query academic research papers using natural language. Instead of reading through hundreds of pages, you simply ask a question and get a precise answer with the exact source citation — paper name and page number.

**Problem it solves:** Reading and extracting information from research papers is time consuming. Researchers, students, and engineers often need quick answers from multiple papers simultaneously. This copilot acts as an intelligent research assistant that has read all your papers and can answer questions instantly.

**Why it's useful:**
- No more manually searching through PDFs
- Answers are always grounded in the actual paper content
- Cite exactly which paper and page the answer comes from
- Add any arXiv paper in seconds directly from the browser

---

## 🚀 Features

- Fetch papers automatically from arXiv by paper ID
- Add papers directly from the browser — no terminal needed
- Semantic search across all ingested papers simultaneously
- Grounded answers with page level citations
- Incremental ingestion — add new papers without rebuilding index
- Clear and rebuild index from the UI
- Cross paper questions — ask across multiple papers at once
- REST API backend — easily extensible
- Evaluation pipeline using RAGAs metrics

---

## 🛠️ Tech Stack

| Layer            | Technology                                      |
|------------------|-------------------------------------------------|
| Language         | Python 3.11+                                    |
| LLM              | Llama 3 via Groq API (free)                     |
| Embeddings       | all-MiniLM-L6-v2 via HuggingFace (free, local)  |
| Vector Database  | FAISS                                           |
| Orchestration    | LangChain                                       |
| Backend          | FastAPI                                         |
| Frontend         | Streamlit                                       |
| Evaluation       | RAGAs                                           |
| Containerization | Docker                                          |

---
