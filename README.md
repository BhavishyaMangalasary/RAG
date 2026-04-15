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
- In the sidebar, type an arXiv ID e.g. 1706.03762
- Click Fetch + Ingest
- Wait ~30 seconds
- Ask questions in the chat box

---

## 📁 Project Structure

```bash
rag-research-copilot/
│
├── src/
│   ├── config.py       # all settings loaded from .env
│   ├── fetcher.py      # downloads papers from arXiv API
│   ├── ingest.py       # chunks, embeds, builds FAISS index
│   ├── retriever.py    # searches FAISS for relevant chunks
│   ├── chain.py        # connects retriever to Llama 3
│   └── api.py          # FastAPI backend with all endpoints
│
├── eval/
│   └── evaluate.py     # RAGAs quality evaluation
│
├── app.py              # Streamlit chat UI
├── requirements.txt    # all dependencies
├── Dockerfile          # containerization
├── .env.example        # environment variables template
└── README.md
```

---

## 📊 Results / Output

### Sample answer with citation

Q: What is multi-head attention?
A: Multi-head attention runs the attention mechanism multiple
times in parallel with different learned projections,
allowing the model to jointly attend to information from
different representation subspaces at different positions.
Sources:

- attention_is_all_you_need.pdf (page 4)
- attention_is_all_you_need.pdf (page 5)

<img width="1790" height="1032" alt="image" src="https://github.com/user-attachments/assets/2f3c4a2e-40f1-4abe-a6b8-6ac990f7dc0e" />

---

## 👤 Author

**Bhavishya**

---

## 🌟 Acknowledgements

- [LangChain](https://langchain.com) for the RAG orchestration framework
- [Groq](https://console.groq.com) for free Llama 3 inference
- [HuggingFace](https://huggingface.co) for free local embeddings
- [FAISS](https://github.com/facebookresearch/faiss) for vector similarity search
- [arXiv](https://arxiv.org) for free access to research papers
