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

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- Free Groq API key from [console.groq.com](https://console.groq.com)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/rag-research-copilot
cd rag-research-copilot

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Open .env and paste your GROQ_API_KEY
```

---

## 🚀 Usage

### Start the app

```bash
# Terminal 1 — start the API
uvicorn src.api:app --reload --port 8000

# Terminal 2 — start the UI
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### Add papers and ask questions
